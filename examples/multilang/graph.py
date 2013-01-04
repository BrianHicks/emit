from emit import Router
from emit.multilang import MultiLangNode

router = Router()

@router.node(['n'])
class PythonShellNode(MultiLangNode):
    command = 'python test.py'

@router.node(['n'])
class RubyShellNode(MultiLangNode):
    command = 'bundle exec ruby test.rb'
