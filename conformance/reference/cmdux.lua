local source = assert(vim.env.CMDUX_SOURCE, "CMDUX_SOURCE is required")
vim.opt.runtimepath:prepend(source)
package.path = source .. "/lua/?.lua;" .. source .. "/lua/?/init.lua;" .. package.path
vim.g.cmdux_disable_blocklist_live_validation = true

local file = assert(io.open(vim.env.CMDUX_CASE, "r"))
local fixture = vim.json.decode(file:read("*a"))
file:close()
local cmdux = require("cmdux")
local types = require("cmdux.types")
local resolver = require("cmdux.lib.resolver")
local learning = require("cmdux.lib.learning")
local completion = require("cmdux.lib.completion")
cmdux.setup()

local by_id = {}
local function remember(node, ancestors)
	by_id[node.id] = node
	node.line = table.concat(vim.list_extend(vim.deepcopy(ancestors), { node.token }), " ")
	local next_ancestors = vim.list_extend(vim.deepcopy(ancestors), { node.token })
	for _, child in ipairs(node.children or {}) do
		remember(child, next_ancestors)
	end
end
local function node_spec(node)
	local slots = {}
	for _, child in ipairs(node.children or {}) do
		if child.kind == "slot" then
			slots[#slots + 1] = { name = child.token:sub(2), kind = child.slot_kind, required = true }
		end
	end
	return {
		token = node.token,
		label = node.token,
		kind = node.kind,
		executable = node.kind == "leaf" or node.kind == "hybrid",
		requires_more = node.kind == "namespace",
		slots = slots,
	}
end
local function register(root)
	remember(root, {})
	assert(cmdux.register_command(root.token, {
		id = "fixture_" .. root.token,
		persistable_nodes = true,
		describe_root = function()
			return types.node(node_spec(root))
		end,
		resolve = function(ctx)
			local node = root
			for _, token in ipairs(ctx.accepted) do
				local found
				for _, child in ipairs(node.children or {}) do
					if child.token == token then
						found = child
						break
					end
				end
				if not found and node.children and node.children[1] and node.children[1].kind == "slot" then
					return types.state_from_node(
						types.node(node_spec(node)),
						{ mode = "slot_edit", executable = true, requires_more = false, slot_values = { token } }
					)
				end
				if not found then
					return types.state_from_node(
						types.node(node_spec(node)),
						{ executable = false, requires_more = false }
					)
				end
				node = found
			end
			if node.children and node.children[1] and node.children[1].kind == "slot" then
				local frontier = {}
				for _, value in ipairs(node.children[1].values or {}) do
					if ctx.pending == "" or value:sub(1, #ctx.pending) == ctx.pending then
						frontier[#frontier + 1] =
							types.frontier_item({ token = value, label = value, kind = "arg", executable = true })
					end
				end
				local slot_state = {
					mode = "slot_edit",
					slot_values = ctx.pending ~= "" and { ctx.pending } or {},
					frontier = frontier,
				}
				return types.state_from_node(types.node(node_spec(node)), slot_state)
			end
			local frontier = {}
			for _, child in ipairs(node.children or {}) do
				if ctx.pending == "" or child.token:sub(1, #ctx.pending) == ctx.pending then
					local spec = node_spec(child)
					spec.node_id = child.id
					frontier[#frontier + 1] = types.frontier_item(spec)
				end
			end
			return types.state_from_node(types.node(node_spec(node)), { frontier = frontier })
		end,
	}))
end
for _, root in ipairs(fixture.tree or {}) do
	register(root)
end
require("cmdux.index").sync()

local function timestamp(value)
	local y, m, d, hh, mm, ss = value:match("^(%d%d%d%d)%-(%d%d)%-(%d%d)T(%d%d):(%d%d):(%d%d)Z$")
	assert(y, "invalid timestamp " .. value)
	return os.time({
		year = tonumber(y),
		month = tonumber(m),
		day = tonumber(d),
		hour = tonumber(hh),
		min = tonumber(mm),
		sec = tonumber(ss),
	})
end
local function set_context(ctx)
	local dir = vim.env.CMDUX_FIXTURE_DIR .. "/projects/" .. ctx.project
	vim.fn.mkdir(dir, "p")
	vim.cmd("lcd " .. vim.fn.fnameescape(dir))
	vim.bo.filetype = ctx.resource
end
local function events_for(session)
	for _, event in ipairs(fixture.events or {}) do
		if event.session == session then
			learning.set_now_for_tests(timestamp(event.time))
			set_context(event.context)
			local node = assert(by_id[event.node])
			local line = node.line
			if node.kind == "slot" then
				line = line:sub(1, #line - #node.token) .. assert(node.values[1])
			end
			local state = resolver.resolve_line(line)
			assert(state.root and state.executable, "not executable: " .. event.node .. " " .. vim.inspect(state))
			learning.record_execute_state(state, { surface = event.surface, shortcut = event.surface == "shortcut" })
		end
	end
end
if fixture.type == "ranking" then
	if vim.env.CMDUX_PHASE == "previous" then
		events_for("previous")
	else
		learning.set_now_for_tests(timestamp(fixture.query.time))
		learning.reload()
		events_for("current")
		learning.set_now_for_tests(timestamp(fixture.query.time))
		set_context(fixture.query.context)
		local state
		if fixture.query.parent == vim.NIL then
			local roots = {}
			for _, root in ipairs(fixture.tree) do
				local spec = node_spec(root)
				spec.node_id = root.id
				roots[#roots + 1] = types.frontier_item(spec)
			end
			state = types.root_state({ raw = "", pending = "", frontier = roots })
		else
			state = resolver.resolve_line(assert(by_id[fixture.query.parent]).line .. " ")
		end
		local ranked = learning.rank_state(state)
		local choices, promotions = {}, {}
		for _, item in ipairs(ranked.frontier) do
			if item.promoted then
				promotions[#promotions + 1] = item.node_id
			else
				choices[#choices + 1] = item.node_id
			end
		end
		io.write(vim.json.encode({ choices = choices, promotions = promotions }), "\n")
	end
elseif vim.env.CMDUX_PHASE == "query" then
	local before = fixture.input.line:sub(1, fixture.input.cursor)
	local state = resolver.resolve_line(before)
	local choice = fixture.input.choice
	if fixture.input.select_from_frontier then
		choice = nil
		for _, item in ipairs(state.frontier) do
			if item.token == fixture.input.choice then
				choice = item
				break
			end
		end
		assert(choice, "slot choice absent from frontier: " .. vim.inspect(state))
	end
	local edit =
		assert(completion.edit(state, choice, fixture.input.line, fixture.input.cursor, fixture.input.replace_root))
	io.write(
		vim.json.encode({ line = completion.apply(fixture.input.line, edit), cursor = edit.start + #edit.text }),
		"\n"
	)
end
