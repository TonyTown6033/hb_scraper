# 修复 Neovim/Neovide 自动格式化问题

## 问题原因

你的 Neovim 配置了自动格式化工具（如 black、ruff），默认行长度为 88 字符，会自动将长行代码换行，但有时会导致语法错误，特别是 f-string。

## 解决方案

### 方案1：调整项目行长度限制（推荐）

已经在项目中创建了配置文件：

**pyproject.toml** - 设置行长度为 120
```toml
[tool.black]
line-length = 120

[tool.ruff]
line-length = 120
```

**.editorconfig** - 统一编辑器配置
```ini
[*.py]
max_line_length = 120
```

### 方案2：修改 Neovim 配置

在你的 Neovim 配置文件中（通常是 `~/.config/nvim/init.lua` 或 `~/.config/nvim/init.vim`）：

#### 如果使用 null-ls（或 none-ls）

```lua
-- 在 null-ls 配置中
local null_ls = require("null-ls")

null_ls.setup({
    sources = {
        -- Black 格式化器，设置行长度
        null_ls.builtins.formatting.black.with({
            extra_args = { "--line-length", "120" }
        }),

        -- 或使用 Ruff
        null_ls.builtins.formatting.ruff.with({
            extra_args = { "--line-length", "120" }
        }),
    },
})
```

#### 如果使用 conform.nvim

```lua
require("conform").setup({
    formatters_by_ft = {
        python = { "black" },
    },
    formatters = {
        black = {
            prepend_args = { "--line-length", "120" },
        },
    },
})
```

#### 如果使用 LSP (pyright/pylsp)

```lua
require('lspconfig').pyright.setup({
    settings = {
        python = {
            formatting = {
                provider = "black",
            },
        },
    },
})
```

### 方案3：禁用保存时自动格式化

如果你想手动控制格式化：

```lua
-- 禁用保存时自动格式化
vim.api.nvim_create_autocmd("BufWritePre", {
    pattern = "*.py",
    callback = function()
        -- 不执行格式化
    end,
})
```

或者创建快捷键手动格式化：

```lua
-- 按 <leader>f 手动格式化
vim.keymap.set("n", "<leader>f", function()
    vim.lsp.buf.format({ async = true })
end, { desc = "Format file" })
```

### 方案4：针对特定代码禁用格式化

在代码中使用注释：

```python
# fmt: off  # 禁用 black 格式化
details["directions"] = f"{directions.get('heading', '')} {directions.get('text', '')}".strip()
# fmt: on   # 恢复格式化
```

或者使用 ruff：

```python
# ruff: noqa
details["directions"] = f"{directions.get('heading', '')} {directions.get('text', '')}".strip()
```

## 推荐配置

1. **使用项目级配置**（已完成）
   - ✅ `pyproject.toml` - 行长度 120
   - ✅ `.editorconfig` - 统一编辑器设置

2. **修改 Neovim 全局配置**
   - 将格式化工具的行长度设置为 120
   - 或者禁用保存时自动格式化

3. **代码风格建议**
   - 对于复杂的 f-string，先提取变量再拼接
   - 这样既避免格式化问题，也提高代码可读性

```python
# 好的做法 ✅
heading = directions.get('heading', '')
text = directions.get('text', '')
details["directions"] = f"{heading} {text}".strip()

# 避免的做法 ⚠️
details["directions"] = f"{directions.get('heading', '')} {directions.get('text', '')}".strip()
```

## 验证配置

运行以下命令检查配置是否生效：

```bash
# 检查 black 配置
uv run black --line-length 120 --check main.py

# 检查 ruff 配置
uv run ruff format --line-length 120 --check main.py
```

## 相关文件

- `pyproject.toml` - Python 项目配置
- `.editorconfig` - 编辑器配置
- `~/.config/nvim/init.lua` - Neovim 配置
