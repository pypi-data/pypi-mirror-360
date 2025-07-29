#❯ pycodetags --help
#usage: pycodetags [-h] {report,plugin-info,jira-sync} ...
#
#TODOs in source code as a first class construct (v0.1.0)
#
#positional arguments:
#  {report,plugin-info,jira-sync}
#                        Available commands
#    report              Generate code tag reports
#    plugin-info         Display information about loaded plugins
#    jira-sync           Synchronize TODOs with Jira
#
#options:
#  -h, --help            show this help message and exit
set -e
export PYCODETAGS_NO_OPEN_BROWSER=1
make install_plugins
#echo "JS plugin"
#pycodetags report --src demo/demo.js
#echo "Report plugin"
#pycodetags report  --module demo.__main__ --src demo --format markdown_simple
echo "Mock integration plugin"
pycodetags github-issues-sync --project foo --dry-run
echo "Mock integration plugin"
pycodetags github-issues-sync --project foo

pycodetags issues  --module demo.__main__ --src demo --format changelog>demo_reports/CHANGELOG.md
echo "-------------------------------------"
pycodetags issues  --module demo.__main__ --src demo --format todomd>demo_reports/todo.md
