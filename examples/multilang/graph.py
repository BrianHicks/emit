from emit import Router
from emit.multilang import ShellNode

router = Router()

@router.node(['n'])
class PythonShellNode(ShellNode):
    command = 'python test.py'

@router.node(['n'])
class RubyShellNode(ShellNode):
    command = 'bundle exec ruby test.rb'
