"""LightHope CLI Tools - 主命令行接口"""

import click
import subprocess
from pathlib import Path
from rich.console import Console
from .version import VERSION

console = Console()

@click.group(invoke_without_command=True)
@click.version_option(version=VERSION, prog_name="lhcli")
@click.pass_context
def cli(ctx):
    """LightHope CLI Tools - 企业级开发工具集"""
    if ctx.invoked_subcommand is None:
        console.print("[bold cyan]LightHope CLI Tools[/bold cyan]")
        console.print(f"Version: {VERSION}")
        console.print("\n使用 [bold]lh --help[/bold] 查看所有命令")

@cli.group()
def diagram():
    """图表生成工具集"""
    pass

@diagram.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='输出文件名')
def mermaid(input_file, output):
    """Mermaid 图表生成
    
    示例：
        lh diagram mermaid flowchart.mmd
        lh diagram mermaid flowchart.mmd -o output.svg
    """
    from pathlib import Path
    
    input_path = Path(input_file)
    output_path = Path(output) if output else input_path.with_suffix('.svg')
    
    # 创建配置目录
    config_dir = Path.home() / '.lhcli'
    config_dir.mkdir(exist_ok=True)
    
    # 创建 puppeteer 配置
    config_file = config_dir / 'puppeteer-config.cjs'
    if not config_file.exists():
        config_file.write_text('{"args": ["--no-sandbox", "--disable-setuid-sandbox"]}')
    
    # 构建命令
    cmd = [
        'mmdc',
        '-i', str(input_path),
        '-o', str(output_path),
        '--puppeteerConfigFile', str(config_file)
    ]
    
    with console.status(f"[cyan]生成图表: {input_file}...[/cyan]"):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                console.print(f"✅ 成功生成: [green]{output_path}[/green]")
            else:
                console.print(f"❌ 生成失败", style="red")
                if result.stderr:
                    console.print(result.stderr, style="dim")
        except FileNotFoundError:
            console.print("❌ 未找到 mmdc 命令", style="red")
            console.print("请安装: [cyan]npm install -g @mermaid-js/mermaid-cli[/cyan]")

def main():
    """主入口"""
    cli()

if __name__ == '__main__':
    main()
# 添加实用功能
@cli.command()
def info():
    """显示系统信息"""
    console.print("[cyan]LightHope CLI Tools[/cyan]")
    console.print(f"Version: {VERSION}")
    console.print(f"Python: {sys.version}")
    console.print(f"User: {os.getenv(USER)}")


@cli.command()
def hello():
    """测试命令"""
    console.print("[bold green]Hello from LightHope CLI! 🚀[/bold green]")
