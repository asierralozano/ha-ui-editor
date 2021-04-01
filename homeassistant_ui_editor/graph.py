from PySide2 import QtCore, QtGui
from homeassistant_ui_editor.lib.NodeGraphQt import NodeGraph, setup_context_menu
from homeassistant_ui_editor.nodes.core_nodes.node_base import HomeAssistantVisualNode
from homeassistant_ui_editor.ui.code_editor import QCodeEditor

from homeassistant_ui_editor.settings import HomeAssistantUIEditorDialog
# from example_auto_nodes import RootNode, Publish, setup_node_menu


class HomeAssistantUIEditorGraph(NodeGraph):

    def __init__(self):
        super(HomeAssistantUIEditorGraph, self).__init__()

        # self.node_double_clicked.connect(self._node_double_clicked)
        # self.add_node(RootNode())
        # setup_context_menu(self)
        # setup_node_menu(self, Publish)
        self.use_OpenGL()
        self.setup_graph_menu()
        self.setup_node_menu(HomeAssistantVisualNode)
        # self._connect_signals()

    # def _connect_signals(self):
    #     self.node_selected.connect(self._node_selected)

    def _create_edit_menu(self, root_menu):
        edit_menu = root_menu.add_menu('&Edit')

        undo_actn = self.undo_stack().createUndoAction(self.viewer(), '&Undo')
        # if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
        undo_actn.setShortcutVisibleInContextMenu(True)
        undo_actn.setShortcuts(QtGui.QKeySequence.Undo)
        edit_menu.qmenu.addAction(undo_actn)

        redo_actn = self.undo_stack().createRedoAction(self.viewer(), '&Redo')
        # if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
        redo_actn.setShortcutVisibleInContextMenu(True)
        redo_actn.setShortcuts(QtGui.QKeySequence.Redo)
        edit_menu.qmenu.addAction(redo_actn)

        edit_menu.add_separator()
        edit_menu.add_command('Clear Undo History', self._clear_undo)
        edit_menu.add_command('Show Undo View', self._show_undo_view)
        edit_menu.add_separator()

        edit_menu.add_command('Copy', self._copy_nodes, QtGui.QKeySequence.Copy)
        edit_menu.add_command('Cut', self._cut_nodes, QtGui.QKeySequence.Cut)
        edit_menu.add_command('Paste', self._paste_nodes, QtGui.QKeySequence.Paste)
        edit_menu.add_command('Delete', self._delete_items, QtGui.QKeySequence.Delete)

        edit_menu.add_separator()

        edit_menu.add_command('Select all', self._select_all_nodes, 'Ctrl+A')
        edit_menu.add_command('Deselect all', self._clear_node_selection, 'Ctrl+Shift+A')
        # edit_menu.add_command('Enable/Disable', _disable_nodes, 'D')

        edit_menu.add_command('Duplicate', self._duplicate_nodes, 'Ctrl+D')
        edit_menu.add_command('Center Selection', self._fit_to_selection, 'F')

        # edit_menu.add_separator()
        #
        # edit_menu.add_command('Layout Graph Up Stream', _layout_graph_up, 'L')
        # edit_menu.add_command('Layout Graph Down Stream', _layout_graph_down, 'Ctrl+L')

        # edit_menu.add_separator()
        #
        # edit_menu.add_command('Jump In', self._jump_in, 'I')
        # edit_menu.add_command('Jump Out', self._jump_out, 'O')

        edit_menu.add_separator()

        # pipe_menu = edit_menu.add_menu('&Pipe')
        # pipe_menu.add_command('Curved Pipe', self._curved_pipe)
        # pipe_menu.add_command('Straight Pipe', self._straight_pipe)
        # pipe_menu.add_command('Angle Pipe', self._angle_pipe)

        bg_menu = edit_menu.add_menu('&Grid Mode')
        bg_menu.add_command('None', self._bg_grid_none)
        bg_menu.add_command('Lines', self._bg_grid_lines)
        bg_menu.add_command('Dots', self._bg_grid_dots)

        edit_menu.add_separator()

        edit_menu.add_command("Preferences", self._open_preferences, "Ctrl+P")

        return edit_menu

    def _open_preferences(self):
        dialog = HomeAssistantUIEditorDialog()
        dialog.exec_()

    def setup_graph_menu(self):
        root_menu = self.context_menu()

        file_menu = root_menu.add_menu('&File')

        # create "File" menu.
        file_menu.add_command('Open...', self._open_session, QtGui.QKeySequence.Open)
        file_menu.add_command('Import...', self._import_session)
        file_menu.add_command('Save...', self._save_session, QtGui.QKeySequence.Save)
        file_menu.add_command('Save As...', self._save_session_as, 'Ctrl+Shift+S')
        file_menu.add_command('New Session', self._new_session)

        file_menu.add_separator()

        file_menu.add_command('Zoom In', self._zoom_in, '=')
        file_menu.add_command('Zoom Out', self._zoom_out, '-')
        file_menu.add_command('Reset Zoom', self._reset_zoom, 'H')

        self._create_edit_menu(root_menu)

    def setup_node_menu(self, published_node_class):
        node_menu = self.context_nodes_menu()
        # test_menu = node_menu.add_menu("asdasd")
        # test_menu.add_command('Zoom In', self._zoom_in, '=')

        node_menu.add_command('Generate Code', self.generate_code, node_class=published_node_class)
        # node_menu.add_command('Generate Code', self.generate_code, node_class=published_node_class)

    def generate_code(self, __, node):
        node_editor = QCodeEditor()
        node_editor.setPlainText(node.run())
        node_editor.show()

    def _zoom_in(self):
        """
        Set the node graph to zoom in by 0.1

        Args:
            graph (NodeGraphQt.NodeGraph): node graph.
        """
        zoom = self.get_zoom() + 0.1
        self.set_zoom(zoom)


    def _zoom_out(self):
        """
        Set the node graph to zoom in by 0.1

        Args:
            graph (NodeGraphQt.NodeGraph): node self.
        """
        zoom = self.get_zoom() - 0.2
        self.set_zoom(zoom)


    def _reset_zoom(self):
        self.reset_zoom()


    def _open_session(self):
        """
        Prompts a file open dialog to load a session.

        Args:
            graph (NodeGraphQt.NodeGraph): node self.
        """
        current = self.current_session()
        viewer = self.viewer()
        file_path = viewer.load_dialog(current)
        if file_path:
            self.load_session(file_path)


    def _import_session(self):
        """
        Prompts a file open dialog to load a session.

        Args:
            graph (NodeGraphQt.NodeGraph): node self.
        """
        current = self.current_session()
        viewer = self.viewer()
        file_path = viewer.load_dialog(current)
        if file_path:
            self.import_session(file_path)


    def _save_session(self):
        """
        Prompts a file save dialog to serialize a session if required.

        Args:
            graph (NodeGraphQt.NodeGraph): node self.
        """
        current = self.current_session()
        if current:
            self.save_session(current)
            msg = 'Session layout saved:\n{}'.format(current)
            viewer = self.viewer()
            viewer.message_dialog(msg, title='Session Saved')
        else:
            self._save_session_as(self)


    def _save_session_as(self):
        """
        Prompts a file save dialog to serialize a session.

        Args:
            graph (NodeGraphQt.NodeGraph): node self.
        """
        current = self.current_session()
        viewer = self.viewer()
        file_path = viewer.save_dialog(current)
        if file_path:
            self.save_session(file_path)


    def _new_session(self):
        """
        Prompts a warning dialog to new a node graph session.

        Args:
            graph (NodeGraphQt.NodeGraph): node self.
        """
        viewer = self.viewer()
        if viewer.question_dialog('Clear Current Session?', 'Clear Session'):
            self.clear_session()


    def _clear_undo(self):
        """
        Prompts a warning dialog to clear undo.

        Args:
            graph (NodeGraphQt.NodeGraph): node self.
        """
        viewer = self.viewer()
        msg = 'Clear all undo history, Are you sure?'
        if viewer.question_dialog('Clear Undo History', msg):
            self.clear_undo_stack()


    def _copy_nodes(self):
        self.copy_nodes()


    def _cut_nodes(self):
        self.cut_nodes()


    def _paste_nodes(self):
        self.paste_nodes()


    def _delete_items(self):
        self.delete_nodes(self.selected_nodes())
        self.delete_pipes(self._viewer.selected_pipes())


    def _select_all_nodes(self):
        self.select_all()


    def _clear_node_selection(self):
        self.clear_selection()


    def _disable_nodes(self):
        self.disable_nodes(self.selected_nodes())


    def _duplicate_nodes(self):
        self.duplicate_nodes(self.selected_nodes())


    def _fit_to_selection(self):
        self.fit_to_selection()


    def _jump_in(self):
        nodes = self.selected_nodes()
        if nodes:
            self.set_node_space(nodes[0])


    def _jump_out(self):
        node = self.get_node_space()
        if node:
            if node.parent() is not None:
                self.set_node_space(node.parent())


    def _show_undo_view(self):
        self.undo_view.show()


    # def _curved_pipe(self):
    #     self.set_pipe_style(PIPE_LAYOUT_CURVED)
    #
    #
    # def _straight_pipe(self):
    #     self.set_pipe_style(PIPE_LAYOUT_STRAIGHT)
    #
    #
    # def _angle_pipe(self):
    #     self.set_pipe_style(PIPE_LAYOUT_ANGLE)


    def _bg_grid_none(self):
        self.set_grid_mode(0)


    def _bg_grid_dots(self):
        self.set_grid_mode(1)


    def _bg_grid_lines(self):
        self.set_grid_mode(2)

    #
    # def __layout_graph(self, down_stream=True):
    #     self.begin_undo('Auto Layout')
    #     node_space = self.get_node_space()
    #     if node_space is not None:
    #         nodes = node_space.children()
    #     else:
    #         nodes = self.all_nodes()
    #     if not nodes:
    #         return
    #     node_views = [n.view for n in nodes]
    #     nodes_center0 = self.viewer().nodes_rect_center(node_views)
    #     if down_stream:
    #         auto_layout_down(all_nodes=nodes)
    #     else:
    #         auto_layout_up(all_nodes=nodes)
    #     nodes_center1 = self.viewer().nodes_rect_center(node_views)
    #     dx = nodes_center0[0] - nodes_center1[0]
    #     dy = nodes_center0[1] - nodes_center1[1]
    #     [n.set_pos(n.x_pos() + dx, n.y_pos()+dy) for n in nodes]
    #     self.end_undo()
    #
    #
    # def _layout_graph_down(self):
    #     __layout_graph(self, True)
    #
    #
    # def _layout_graph_up(self):
    #     __layout_graph(self, False)

    # def _node_double_clicked(self, node):
    #     print(node.render())

