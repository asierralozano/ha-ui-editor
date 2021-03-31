#!/usr/bin/python

from .node_abstract import AbstractNodeItem
from .node_text_item import NodeTextItem
from .port import PortItem, CustomPortItem
from .. import QtGui, QtCore, QtWidgets
from ..constants import (IN_PORT, OUT_PORT,
                         NODE_WIDTH, NODE_HEIGHT,
                         NODE_ICON_SIZE, ICON_NODE_BASE,
                         NODE_SEL_COLOR, NODE_SEL_BORDER_COLOR,
                         PORT_FALLOFF, Z_VAL_NODE, Z_VAL_NODE_WIDGET,
                         ITEM_CACHE_MODE)
from ..errors import NodeWidgetError


class XDisabledItem(QtWidgets.QGraphicsItem):
    """
    Node disabled overlay item.

    Args:
        parent (NodeItem): the parent node item.
        text (str): disable overlay text.
    """

    def __init__(self, parent=None, text=None):
        super(XDisabledItem, self).__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET + 2)
        self.setVisible(False)
        self.color = (0, 0, 0, 255)
        self.text = text

    def boundingRect(self):
        return self.parentItem().boundingRect()

    def paint(self, painter, option, widget):
        """
        Draws the overlay disabled X item on top of a node item.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()

        margin = 20
        rect = self.boundingRect()
        dis_rect = QtCore.QRectF(rect.left() - (margin / 2),
                                 rect.top() - (margin / 2),
                                 rect.width() + margin,
                                 rect.height() + margin)
        pen = QtGui.QPen(QtGui.QColor(*self.color), 8)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(dis_rect.topLeft(), dis_rect.bottomRight())
        painter.drawLine(dis_rect.topRight(), dis_rect.bottomLeft())

        bg_color = QtGui.QColor(*self.color)
        bg_color.setAlpha(100)
        bg_margin = -0.5
        bg_rect = QtCore.QRectF(dis_rect.left() - (bg_margin / 2),
                                dis_rect.top() - (bg_margin / 2),
                                dis_rect.width() + bg_margin,
                                dis_rect.height() + bg_margin)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(bg_rect, 5, 5)

        pen = QtGui.QPen(QtGui.QColor(155, 0, 0, 255), 0.7)
        painter.setPen(pen)
        painter.drawLine(dis_rect.topLeft(), dis_rect.bottomRight())
        painter.drawLine(dis_rect.topRight(), dis_rect.bottomLeft())

        point_size = 4.0
        point_pos = (dis_rect.topLeft(), dis_rect.topRight(),
                     dis_rect.bottomLeft(), dis_rect.bottomRight())
        painter.setBrush(QtGui.QColor(255, 0, 0, 255))
        for p in point_pos:
            p.setX(p.x() - (point_size / 2))
            p.setY(p.y() - (point_size / 2))
            point_rect = QtCore.QRectF(
                p, QtCore.QSizeF(point_size, point_size))
            painter.drawEllipse(point_rect)

        if self.text:
            font = painter.font()
            font.setPointSize(10)

            painter.setFont(font)
            font_metrics = QtGui.QFontMetrics(font)
            font_width = font_metrics.width(self.text)
            font_height = font_metrics.height()
            txt_w = font_width * 1.25
            txt_h = font_height * 2.25
            text_bg_rect = QtCore.QRectF((rect.width() / 2) - (txt_w / 2),
                                         (rect.height() / 2) - (txt_h / 2),
                                         txt_w, txt_h)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 0.5))
            painter.setBrush(QtGui.QColor(*self.color))
            painter.drawRoundedRect(text_bg_rect, 2, 2)

            text_rect = QtCore.QRectF((rect.width() / 2) - (font_width / 2),
                                      (rect.height() / 2) - (font_height / 2),
                                      txt_w * 2, font_height * 2)

            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 1))
            painter.drawText(text_rect, self.text)

        painter.restore()


class NodeItem(AbstractNodeItem):
    """
    Base Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='node', parent=None):
        super(NodeItem, self).__init__(name, parent)
        pixmap = QtGui.QPixmap(ICON_NODE_BASE)
        if pixmap.size().height() > NODE_ICON_SIZE:
            pixmap = pixmap.scaledToHeight(NODE_ICON_SIZE,
                                           QtCore.Qt.SmoothTransformation)
        self._properties['icon'] = ICON_NODE_BASE
        self._icon_item = QtWidgets.QGraphicsPixmapItem(pixmap, self)
        self._icon_item.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self._text_item = NodeTextItem(self.name, self)
        self._x_item = XDisabledItem(self, 'DISABLED')
        self._input_items = {}
        self._output_items = {}
        self._widgets = {}
        self._proxy_mode = False
        self._proxy_mode_threshold = 70
        self._extra_width = 0

    def paint(self, painter, option, widget):
        """
        Draws the node base not the ports.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        self.auto_switch_mode()

        painter.save()
        bg_border = 1.0
        rect = QtCore.QRectF(0.5 - (bg_border / 2),
                             0.5 - (bg_border / 2),
                             self._width + bg_border,
                             self._height + bg_border)
        radius = 2
        border_color = QtGui.QColor(*self.border_color)

        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        rect = self.boundingRect()

        bg_color = QtGui.QColor(*self.color)
        painter.setBrush(bg_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        if self.selected and NODE_SEL_COLOR:
            painter.setBrush(QtGui.QColor(*NODE_SEL_COLOR))
            painter.drawRoundedRect(rect, radius, radius)

        label_rect = QtCore.QRectF(rect.left(), rect.top(), self._width, 28)
        path = QtGui.QPainterPath()
        path.addRoundedRect(label_rect, radius, radius)
        painter.setBrush(QtGui.QColor(30, 30, 30, 200))
        painter.fillPath(path, painter.brush())

        border_width = 0.8
        if self.selected and NODE_SEL_BORDER_COLOR:
            border_width = 1.2
            border_color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
        border_rect = QtCore.QRectF(rect.left() - (border_width / 2),
                                    rect.top() - (border_width / 2),
                                    rect.width() + border_width,
                                    rect.height() + border_width)

        pen = QtGui.QPen(border_color, border_width)
        pen.setCosmetic(self.viewer().get_zoom() < 0.0)
        path = QtGui.QPainterPath()
        path.addRoundedRect(border_rect, radius, radius)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.restore()

    def mousePressEvent(self, event):
        """
        Re-implemented to ignore event if LMB is over port collision area.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        if event.button() == QtCore.Qt.LeftButton:
            for p in self._input_items.keys():
                if p.hovered:
                    event.ignore()
                    return
            for p in self._output_items.keys():
                if p.hovered:
                    event.ignore()
                    return
        super(NodeItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            event.ignore()
            return
        super(NodeItem, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """
        Re-implemented to emit "node_double_clicked" signal.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        if event.button() == QtCore.Qt.LeftButton:

            # enable text item edit mode.
            items = self.scene().items(event.scenePos())
            if self._text_item in items:
                self._text_item.set_editable(True)
                self._text_item.setFocus()
                event.ignore()
                return

            viewer = self.viewer()
            if viewer:
                viewer.node_double_clicked.emit(self.id)
        super(NodeItem, self).mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        if change == self.ItemSelectedChange and self.scene():
            self.reset_pipes()
            if value:
                self.highlight_pipes()
            self.setZValue(Z_VAL_NODE)
            if not self.selected:
                self.setZValue(Z_VAL_NODE + 1)

        return super(NodeItem, self).itemChange(change, value)

    def _tooltip_disable(self, state):
        """
        updates the node tooltip when the node is enabled/disabled.

        Args:
            state (bool): node disable state.
        """
        tooltip = '<b>{}</b>'.format(self.name)
        if state:
            tooltip += ' <font color="red"><b>(DISABLED)</b></font>'
        tooltip += '<br/>{}<br/>'.format(self.type_)
        self.setToolTip(tooltip)

    def _set_base_size(self, add_w=0.0, add_h=0.0):
        """
        setup initial base size.

        Args:
            add_w (float): additional width.
            add_h (float): additional height.
        """
        self._width = NODE_WIDTH + self._extra_width
        self._height = NODE_HEIGHT
        width, height = self.calc_size(add_w, add_h)
        if width > self._width:
            self._width = width
        if height > self._height:
            self._height = height

    def _set_text_color(self, color):
        """
        set text color.

        Args:
            color (tuple): color value in (r, g, b, a).
        """
        text_color = QtGui.QColor(*color)
        for port, text in self._input_items.items():
            text.setDefaultTextColor(text_color)
        for port, text in self._output_items.items():
            text.setDefaultTextColor(text_color)
        self._text_item.setDefaultTextColor(text_color)

    def activate_pipes(self):
        """
        active pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.activate()

    def highlight_pipes(self):
        """
        highlight pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.highlight()

    def reset_pipes(self):
        """
        Reset all the pipe colors.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.reset()

    def calc_size(self, add_w=0.0, add_h=0.0):
        """
        Calculates the minimum node size.

        Args:
            add_w (float): additional width.
            add_h (float): additional height.

        Returns:
            tuple(float, float): width, height.
        """
        width = 0
        height = self._text_item.boundingRect().height()

        if self._widgets:
            wid_width = max([
                w.boundingRect().width() for w in self._widgets.values()
            ])
            if width < wid_width:
                width = wid_width

        port_height = 0.0
        if self._input_items:
            port = None
            input_widths = []
            for port, text in self._input_items.items():
                input_width = port.boundingRect().width() - PORT_FALLOFF
                if text.isVisible():
                    input_width += text.boundingRect().width() / 1.5
                input_widths.append(input_width)
            width += max(input_widths)
            if port:
                port_height = port.boundingRect().height()

        if self._output_items:
            port = None
            output_widths = []
            for port, text in self._output_items.items():
                output_width = port.boundingRect().width()
                if text.isVisible():
                    output_width += text.boundingRect().width() / 1.5
                output_widths.append(output_width)
            width += max(output_widths)
            if port:
                port_height = port.boundingRect().height()

        in_count = len([p for p in self.inputs if p.isVisible()])
        out_count = len([p for p in self.outputs if p.isVisible()])
        height += port_height * max([in_count, out_count])
        if self._widgets:
            wid_height = 0.0
            for w in self._widgets.values():
                wid_height += w.boundingRect().height()
            wid_height += wid_height / len(self._widgets.values())
            if wid_height > height:
                height = wid_height

        width += add_w
        height += add_h

        return width, height

    def align_icon(self, h_offset=0.0, v_offset=0.0):
        """
        Align node icon to the default top left of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        x = 2.0 + h_offset
        y = 2.0 + v_offset
        self._icon_item.setPos(x, y)

    def align_label(self, h_offset=0.0, v_offset=0.0):
        """
        Center node label text to the top of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        text_rect = self._text_item.boundingRect()
        text_x = (self._width / 2) - (text_rect.width() / 2)
        text_y = 2.0
        text_x += h_offset
        text_y += v_offset
        self._text_item.setPos(text_x, text_y)

    def align_widgets(self, v_offset=0.0):
        """
        Align node widgets to the default center of the node.

        Args:
            v_offset (float): vertical offset.
        """
        if not self._widgets:
            return
        wid_heights = sum(
            [w.boundingRect().height() for w in self._widgets.values()])
        pos_y = self._height / 2
        pos_y -= wid_heights / 2
        pos_y += v_offset
        for widget in self._widgets.values():
            rect = widget.boundingRect()
            pos_x = (self._width / 2) - (rect.width() / 2)
            widget.setPos(pos_x, pos_y)
            pos_y += rect.height()

    def align_ports(self, v_offset=0.0):
        """
        Align input, output ports in the node layout.

        Args:
            v_offset (float): port vertical offset.
        """
        width = self._width
        txt_offset = PORT_FALLOFF - 2
        spacing = 1

        # adjust input position
        inputs = [p for p in self.inputs if p.isVisible()]
        if inputs:
            port_width = inputs[0].boundingRect().width()
            port_height = inputs[0].boundingRect().height()
            port_x = (port_width / 2) * -1
            port_y = v_offset
            for port in inputs:
                port.setPos(port_x, port_y)
                port_y += port_height + spacing
        # adjust input text position
        for port, text in self._input_items.items():
            if port.isVisible():
                txt_x = port.boundingRect().width() / 2 - txt_offset
                text.setPos(txt_x, port.y() - 1.5)

        # adjust output position
        outputs = [p for p in self.outputs if p.isVisible()]
        if outputs:
            port_width = outputs[0].boundingRect().width()
            port_height = outputs[0].boundingRect().height()
            port_x = width - (port_width / 2)
            port_y = v_offset
            for port in outputs:
                port.setPos(port_x, port_y)
                port_y += port_height + spacing
        # adjust output text position
        for port, text in self._output_items.items():
            if port.isVisible():
                txt_width = text.boundingRect().width() - txt_offset
                txt_x = port.x() - txt_width
                text.setPos(txt_x, port.y() - 1.5)

    def offset_label(self, x=0.0, y=0.0):
        """
        offset the label in the node layout.

        Args:
            x (float): horizontal x offset
            y (float): vertical y offset
        """
        icon_x = self._text_item.pos().x() + x
        icon_y = self._text_item.pos().y() + y
        self._text_item.setPos(icon_x, icon_y)

    def draw_node(self):
        """
        Re-draw the node item in the scene.
        (re-implemented for vertical layout design)
        """
        height = self._text_item.boundingRect().height()
        # setup initial base size.
        self._set_base_size(add_w=0.0, add_h=height)
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- set the initial node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label(h_offset=0.0, v_offset=0.0)
        # arrange icon
        self.align_icon(h_offset=0.0, v_offset=0.0)
        # arrange input and output ports.
        self.align_ports(v_offset=height + (height / 2))
        # arrange node widgets
        self.align_widgets(v_offset=height / 2)

        self.update()

    def post_init(self, viewer=None, pos=None):
        """
        Called after node has been added into the scene.
        Adjust the node layout and form after the node has been added.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): not used
            pos (tuple): cursor position.
        """
        self.draw_node()

        # set initial node position.
        if pos:
            self.xy_pos = pos

    def auto_switch_mode(self):
        """
        Decide whether to draw the node with proxy mode.
        """
        if ITEM_CACHE_MODE is QtWidgets.QGraphicsItem.ItemCoordinateCache:
            return
        rect = self.sceneBoundingRect()
        l = self.viewer().mapToGlobal(self.viewer().mapFromScene(rect.topLeft()))
        r = self.viewer().mapToGlobal(self.viewer().mapFromScene(rect.topRight()))
        # width is the node width in screen
        width = r.x() - l.x()

        self.set_proxy_mode(width < self._proxy_mode_threshold)

    def set_proxy_mode(self, mode):
        """
        Set whether to draw the node with proxy mode.

        Args:
            mode (bool).
        """
        if mode is self._proxy_mode:
            return

        self._proxy_mode = mode

        visible = not mode

        for w in self._widgets.values():
            w.widget.setVisible(visible)
        for port, text in self._input_items.items():
            port.setVisible(visible)
            if text.visible_:
                text.setVisible(visible)

        for port, text in self._output_items.items():
            port.setVisible(visible)
            if text.visible_:
                text.setVisible(visible)

        self._text_item.setVisible(visible)
        self._icon_item.setVisible(visible)

    @property
    def icon(self):
        return self._properties['icon']

    @icon.setter
    def icon(self, path=None):
        self._properties['icon'] = path
        path = path or ICON_NODE_BASE
        pixmap = QtGui.QPixmap(path)
        if pixmap.size().height() > NODE_ICON_SIZE:
            pixmap = pixmap.scaledToHeight(NODE_ICON_SIZE,
                                           QtCore.Qt.SmoothTransformation)
        self._icon_item.setPixmap(pixmap)
        if self.scene():
            self.post_init()

        self.update()

    @AbstractNodeItem.width.setter
    def width(self, width=0.0):
        w, h = self.calc_size()
        width = width if width > w else w
        AbstractNodeItem.width.fset(self, width)

    @AbstractNodeItem.height.setter
    def height(self, height=0.0):
        w, h = self.calc_size()
        h = 70 if h < 70 else h
        height = height if height > h else h
        AbstractNodeItem.height.fset(self, height)

    @AbstractNodeItem.disabled.setter
    def disabled(self, state=False):
        AbstractNodeItem.disabled.fset(self, state)
        for n, w in self._widgets.items():
            w.get_custom_widget().setDisabled(state)
        self._tooltip_disable(state)
        self._x_item.setVisible(state)

    @AbstractNodeItem.selected.setter
    def selected(self, selected=False):
        AbstractNodeItem.selected.fset(self, selected)
        if selected:
            self.highlight_pipes()

    @AbstractNodeItem.name.setter
    def name(self, name=''):
        AbstractNodeItem.name.fset(self, name)
        if name == self._text_item.toPlainText():
            return
        self._text_item.setPlainText(name)
        if self.scene():
            self.align_label()
        self.update()

    @AbstractNodeItem.color.setter
    def color(self, color=(100, 100, 100, 255)):
        AbstractNodeItem.color.fset(self, color)
        if self.scene():
            self.scene().update()
        self.update()

    @AbstractNodeItem.text_color.setter
    def text_color(self, color=(100, 100, 100, 255)):
        AbstractNodeItem.text_color.fset(self, color)
        self._set_text_color(color)
        self.update()

    @property
    def text_item(self):
        """
        Get the node name text qgraphics item.

        Returns:
            NodeTextItem: node text object.
        """
        return self._text_item

    @property
    def inputs(self):
        """
        Returns:
            list[PortItem]: input port graphic items.
        """
        return list(self._input_items.keys())

    @property
    def outputs(self):
        """
        Returns:
            list[PortItem]: output port graphic items.
        """
        return list(self._output_items.keys())

    def _add_port(self, port):
        """
        Adds a port qgraphics item into the node.

        Args:
            port (PortItem): port item.

        Returns:
            PortItem: port qgraphics item.
        """
        text = QtWidgets.QGraphicsTextItem(port.name, self)
        text.font().setPointSize(8)
        text.setFont(text.font())
        text.setVisible(port.display_name)
        text.visible_ = port.display_name
        text.setCacheMode(ITEM_CACHE_MODE)
        if port.port_type == IN_PORT:
            self._input_items[port] = text
        elif port.port_type == OUT_PORT:
            self._output_items[port] = text
        if self.scene():
            self.post_init()
        return port

    def add_port(self, port_type=IN_PORT, name='input', multi_port=False, display_name=True,
                 locked=False, painter_func=None, optional=True, limited_type=None):

        if painter_func:
            port = CustomPortItem(self, painter_func)
        else:
            port = PortItem(self)
        port.name = name
        port.port_type = port_type
        port.multi_connection = multi_port
        port.display_name = display_name
        port.locked = locked
        port.optional = optional
        port.limited_type = limited_type
        return self._add_port(port)

    def add_input(self, name='input', multi_port=False, display_name=True,
                  locked=False, painter_func=None, optional=True, limited_type=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        IN_PORT.

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): display the port name.
            locked (bool): locked state.
            painter_func (function): custom paint function.

        Returns:
            PortItem: input port qgraphics item.
        """
        if painter_func:
            port = CustomPortItem(self, painter_func)
        else:
            port = PortItem(self)
        port.name = name
        port.port_type = IN_PORT
        port.multi_connection = multi_port
        port.display_name = display_name
        port.locked = locked
        port.optional = optional
        port.limited_type = limited_type
        return self._add_port(port)

    def add_output(self, name='output', multi_port=False, display_name=True,
                   locked=False, painter_func=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        OUT_PORT.

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): display the port name.
            locked (bool): locked state.
            painter_func (function): custom paint function.

        Returns:
            PortItem: output port qgraphics item.
        """
        if painter_func:
            port = CustomPortItem(self, painter_func)
        else:
            port = PortItem(self)
        port.name = name
        port.port_type = OUT_PORT
        port.multi_connection = multi_port
        port.display_name = display_name
        port.locked = locked
        return self._add_port(port)

    def _delete_port(self, port, text):
        """
        Removes port item and port text from node.

        Args:
            port (PortItem): port object.
            text (QtWidgets.QGraphicsTextItem): port text object.
        """
        port.delete()
        port.setParentItem(None)
        text.setParentItem(None)
        self.scene().removeItem(port)
        self.scene().removeItem(text)
        del port
        del text

    def delete_input(self, port):
        """
        Remove input port from node.

        Args:
            port (PortItem): port object.
        """
        self._delete_port(port, self._input_items.pop(port))

    def delete_output(self, port):
        """
        Remove output port from node.

        Args:
            port (PortItem): port object.
        """
        self._delete_port(port, self._output_items.pop(port))

    def get_input_text_item(self, port_item):
        """
        Args:
            port_item (PortItem): port item.

        Returns:
            QGraphicsTextItem: graphic item used for the port text.
        """
        return self._input_items[port_item]

    def get_output_text_item(self, port_item):
        """
        Args:
            port_item (PortItem): port item.

        Returns:
            QGraphicsTextItem: graphic item used for the port text.
        """
        return self._output_items[port_item]

    @property
    def widgets(self):
        return self._widgets.copy()

    def add_widget(self, widget):
        self._widgets[widget.get_name()] = widget

    def get_widget(self, name):
        widget = self._widgets.get(name)
        if widget:
            return widget
        raise NodeWidgetError('node has no widget "{}"'.format(name))

    def has_widget(self, name):
        return name in self._widgets.keys()

    def delete(self):
        [port.delete() for port, text in self._input_items.items()]
        [port.delete() for port, text in self._output_items.items()]
        super(NodeItem, self).delete()

    def from_dict(self, node_dict):
        super(NodeItem, self).from_dict(node_dict)
        widgets = node_dict.pop('widgets', {})
        for name, value in widgets.items():
            if self._widgets.get(name):
                self._widgets[name].value = value

    def set_extra_width(self, width):
        self._extra_width = width


class NodeItemVertical(NodeItem):
    """
    Vertical Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='node', parent=None):
        super(NodeItemVertical, self).__init__(name, parent)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.text_item.setFont(font)

    def paint(self, painter, option, widget):
        """
        Draws the node base not the ports.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        self.auto_switch_mode()

        painter.save()
        bg_border = 1.0
        rect = QtCore.QRectF(0.5 - (bg_border / 2),
                             0.5 - (bg_border / 2),
                             self._width + bg_border,
                             self._height + bg_border)
        radius = 2
        border_color = QtGui.QColor(*self.border_color)

        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        rect = self.boundingRect()

        bg_color = QtGui.QColor(*self.color)
        painter.setBrush(bg_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        if self.selected and NODE_SEL_COLOR:
            painter.setBrush(QtGui.QColor(*NODE_SEL_COLOR))
            painter.drawRoundedRect(rect, radius, radius)

        label_rect = QtCore.QRectF(rect.left(), rect.top(), self._width, 15)
        path = QtGui.QPainterPath()
        path.addRoundedRect(label_rect, radius, radius)
        painter.setBrush(QtGui.QColor(30, 30, 30, 200))
        painter.fillPath(path, painter.brush())

        label_rect = QtCore.QRectF(rect.left(), rect.bottom()-15, self._width, 15)
        path = QtGui.QPainterPath()
        path.addRoundedRect(label_rect, radius, radius)
        painter.fillPath(path, painter.brush())

        border_width = 0.8
        if self.selected and NODE_SEL_BORDER_COLOR:
            border_width = 1.2
            border_color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
        border_rect = QtCore.QRectF(rect.left() - (border_width / 2),
                                    rect.top() - (border_width / 2),
                                    rect.width() + border_width,
                                    rect.height() + border_width)

        pen = QtGui.QPen(border_color, border_width)
        pen.setCosmetic(self.viewer().get_zoom() < 0.0)
        path = QtGui.QPainterPath()
        path.addRoundedRect(border_rect, radius, radius)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.restore()

    def align_icon(self, h_offset=0.0, v_offset=0.0):
        """
        Align node icon to the default top left of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        # icon_rect = self._icon_item.boundingRect()
        # x = self._width / 2 - (icon_rect.width() / 2) + h_offset
        # y = self._height / 2 - (icon_rect.height() / 2) + v_offset
        x = 2.0 + h_offset
        y = 17.0 + v_offset
        self._icon_item.setPos(x, y)

    def align_label(self, h_offset=0.0, v_offset=0.0):
        """
        Align node label to the default top center of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        text_rect = self.text_item.boundingRect()
        text_x = self._width + 10 + h_offset
        text_y = self._height / 2 - (text_rect.height() / 2)
        self.text_item.setPos(text_x, text_y)

    def align_ports(self, v_offset=0.0):
        """
        Align input, output ports in the node layout.
        """
        # adjust input position
        inputs = [p for p in self.inputs if p.isVisible()]
        if inputs:
            port_width = inputs[0].boundingRect().width()
            port_height = inputs[0].boundingRect().height()
            half_width = port_width/2
            delta = self._width / (len(inputs)+1)
            port_x = delta
            port_y = (port_height / 2) * -1
            for port in inputs:
                port.setPos(port_x - half_width, port_y)
                port_x += delta

        # adjust output position
        outputs = [p for p in self.outputs if p.isVisible()]
        if outputs:
            port_width = outputs[0].boundingRect().width()
            port_height = outputs[0].boundingRect().height()
            half_width = port_width / 2
            delta = self._width / (len(outputs)+1)
            port_x = delta
            port_y = self._height - (port_height / 2)
            for port in outputs:
                port.setPos(port_x-half_width, port_y)
                port_x += delta

    def draw_node(self):
        """
        Re-draw the node item in the scene.
        """
        # setup initial base size.
        self._set_base_size(add_w=0.0, add_h=0.0)
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- setup node layout ---
        # (do all the graphic item layout offsets here)

        # arrange label text
        self.align_label(h_offset=0.0, v_offset=0.0)
        # arrange icon
        self.align_icon(h_offset=0.0, v_offset=0.0)
        # arrange input and output ports.
        self.align_ports()
        # arrange node widgets
        self.align_widgets(v_offset=0.0)

        self.update()

    def calc_size(self, add_w=0.0, add_h=0.0):
        """
        Calculate minimum node size.

        Args:
            add_w (float): additional width.
            add_h (float): additional height.
        """
        width = 0
        height = 0

        if self._widgets:
            wid_width = max([
                w.boundingRect().width() for w in self._widgets.values()
            ])
            width = max(width, wid_width)

        port_width = 0.0
        if self._input_items:
            port = list(self._input_items.keys())[0]
            height += port.boundingRect().height()
            port_width = port.boundingRect().width()

        if self._output_items:
            port = list(self._output_items.keys())[0]
            height += port.boundingRect().height()
            port_width = port.boundingRect().width()

        in_count = len([p for p in self.inputs if p.isVisible()])
        out_count = len([p for p in self.outputs if p.isVisible()])
        width = max(width, port_width * max(in_count, out_count))
        if self._widgets:
            wid_height = 0.0
            for w in self._widgets.values():
                wid_height += w.boundingRect().height()
            wid_height += wid_height / len(self._widgets.values())
            if wid_height > height:
                height = wid_height

        width += add_w
        height += add_h + 15

        return width, height

    def add_input(self, name='input', multi_port=False, display_name=True,
                  painter_func=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        IN_PORT

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): (not used)
            painter_func (function): custom paint function.

        Returns:
            PortItem: port qgraphics item.
        """
        return super(NodeItemVertical, self).add_input(
            name, multi_port, False, painter_func)

    def add_output(self, name='output', multi_port=False, display_name=False,
                   painter_func=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        OUT_PORT

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): (not used)
            painter_func (function): custom paint function.

        Returns:
            PortItem: port qgraphics item.
        """
        return super(NodeItemVertical, self).add_output(
            name, multi_port, False, painter_func)
