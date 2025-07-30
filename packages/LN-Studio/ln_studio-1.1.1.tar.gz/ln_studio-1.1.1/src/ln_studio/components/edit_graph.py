from functools import partial

import json
import os
import inspect
import yaml

from qtpy.QtWidgets import QHBoxLayout, QWidget
from qtpy.QtCore import Signal
import graphviz

from livenodes import Node, Connection, REGISTRY
from livenodes.components.node_connector import Connectionist

from ln_studio.qtpynodeeditor import FlowScene, FlowView, DataModelRegistry, NodeDataModel, NodeDataType, PortType
from ln_studio.qtpynodeeditor.node_graphics_object import NodeGraphicsObject
from ln_studio.qtpynodeeditor.exceptions import ConnectionDataTypeFailure, MultipleInputConnectionError

from .edit_node import CreateNodeDialog

import logging
logger = logging.getLogger('LN-Studio')

class CustomNodeDataModel(NodeDataModel, verify=False):

    def __init__(self, style=None, parent=None):
        super().__init__(style, parent)
        self.association_to_node = None
        self.flow_scene = None

        # self._info = QLabel("Info")

    def set_node_association(self, pl_node):
        self.association_to_node = pl_node

    def set_flow_scene(self, flow_scene):
        self.flow_scene = flow_scene


    def __getstate__(self) -> dict:
        res = super().__getstate__()
        res['association_to_node'] = self.association_to_node
        return res

    # def embedded_widget(self) -> QWidget:
    #     'The number source has a line edit widget for the user to type in'
    #     return self._info

    # @property
    # def caption(self):
    #     if self.association_to_node is not None:
    #         return str(self.association_to_node.name)
    #     else:
    #         return self.name

    def _get_port_infos(self, connection):
        # TODO: yes, the naming here is confusing, as qtpynode is the other way round that livenodes
        in_port, out_port = connection.ports
        emit_port_label = out_port.model.data_type[out_port.port_type][out_port.index].name
        recv_port_label = in_port.model.data_type[in_port.port_type][in_port.index].name

        ln_studio_receiving_node = in_port.model.association_to_node
        ln_studio_emit_node = out_port.model.association_to_node

        return ln_studio_emit_node, ln_studio_receiving_node, emit_port_label, recv_port_label

    # TODO: do the same for the input connections!
    # Comment: make sure to not then have duplicates in the connections -yh
    # also double check if not all input connections are already handled, since the outputs are handled and a connection always must have both
    # -> might not be the case if a node is deleted -> if the connection is removed than this should be the case, otherwise we might have to implement these two methods
    # input_connection_created
    # input_connection_deleted

    def output_connection_created(self, connection):
        # HACK: this currently works because of the three passes below (ie create node, create conneciton, associate pl node)
        # TODO: fix this by checking if the connection already exists and if so ignore the call
        if self.association_to_node is not None:
            ln_studio_emit_node, ln_studio_receiving_node, emit_port_label, recv_port_label = self._get_port_infos(connection)

            if ln_studio_emit_node is not None and ln_studio_receiving_node is not None:
                # occours when a node was deleted, in which case this is not important anyway
                try:
                    ln_studio_receiving_node.add_input(
                        ln_studio_emit_node,
                        emit_port=ln_studio_emit_node.get_port_out_by_label(emit_port_label),
                        recv_port=ln_studio_receiving_node.get_port_in_by_label(recv_port_label)
                    )
                except ValueError as err:
                    if 'Connection already exists' in str(err):
                        logger.info('Connection already exists. Not adding again.')
                    else:
                        logger.error(err)
                        logger.warning('Removing in qtypynodeeditor as well.')
                        self.flow_scene.delete_connection(connection)


    def output_connection_deleted(self, connection):
        if self.association_to_node is not None:
            ln_studio_emit_node, ln_studio_receiving_node, emit_port_label, recv_port_label = self._get_port_infos(connection)

            if ln_studio_emit_node is not None and ln_studio_receiving_node is not None:
                # occours when a node was deleted, in which case this is not important anyway
                try:
                    ln_studio_receiving_node.remove_input(
                        ln_studio_emit_node,
                        emit_port=ln_studio_emit_node.get_port_out_by_label(emit_port_label),
                        recv_port=ln_studio_receiving_node.get_port_in_by_label(recv_port_label)
                    )
                except ValueError as err:
                    logger.exception('Error in removing connection.')
                    logger.debug(err)
                    # TODO: see nodes above on created...


def attatch_click_cb(node_graphic_ob, cb):
    prev_fn = node_graphic_ob.mousePressEvent

    def new_fn(event):
        cb()
        prev_fn(event)

    node_graphic_ob.mousePressEvent = new_fn
    return node_graphic_ob


class QT_Graph_edit(QWidget):
    node_selected = Signal(Node)

    def __init__(self, pipeline_path, node_registry, parent=None, read_only=False, resolve_macros=False):
        super().__init__(parent)
        # There are two use cases: 
        # 1. The pipeline is newly created and thus empty
        # 2. The pipeline is loaded from a file and thus has nodes

        self.pipeline_path = pipeline_path

        self.known_classes = {}
        self.read_only = read_only
        self.resolve_macros = resolve_macros
        
        self.pipeline_gui_path_debug = pipeline_path.replace('.yml', '_gui_debug.json', 1)
        self.pipeline_gui_path_non_debug = pipeline_path.replace('.yml', '_gui.json', 1)
        if self.resolve_macros:
            self.pipeline_gui_path = self.pipeline_gui_path_debug
        else:
            self.pipeline_gui_path = self.pipeline_gui_path_non_debug

        self._create_known_classes(node_registry)

        # TODO: could this moved be moved to a patch? -yh
        # Would be great if the copy_nodes patch would not rely on this function...
        # ofc we could also adjust that one to not rely on this function here...
        self_alias = self
        def _create_node(self, data_model, pl_node=None, skip_association=False):
            nonlocal self_alias
            if pl_node is None:
                try:
                    msg = CreateNodeDialog(data_model)
                    if msg.exec():
                        pl_node = data_model.constructor(**msg.edit_dict)
                    else:
                        # if the dialog was canceled, we don't want to create a node
                        logger.exception(f'Could not create node: {data_model.name}. Dialog was canceled.')
                        return None
                except Exception as err:
                    # if there is any error in the dialog, we don't want to create a node
                    # e.g. a file not found error in case of macros or similar
                    logger.error(err)
                    logger.exception(f'Could not create node: {data_model.name}. Dialog was canceled.')
                    return None

            new_data_model = self_alias._register_node(pl_node)

            with self._new_node_context(new_data_model.name) as node:
                ngo = NodeGraphicsObject(self, node)
                node.graphics_object = ngo

                if not skip_association:
                    node.model.set_node_association(pl_node)
                    node.model.set_flow_scene(self)
                    node._graphics_obj = attatch_click_cb(
                        node._graphics_obj,
                        partial(self_alias.node_selected.emit, pl_node))
    
            return node

        ### Setup scene
        self.scene = FlowScene(registry=self.registry, 
                            allow_node_creation = not self.read_only, 
                            allow_node_deletion = not self.read_only,
                            allow_edge_creation = not self.read_only,
                            allow_edge_deletion = not self.read_only)
        self.scene.create_node = _create_node.__get__(self.scene, self.scene.__class__)

        self.scene.node_deleted.connect(self._remove_pl_node)

        # self.scene.connection_created.connect(lambda connection: print("Created", connection))
        # self.scene.connection_deleted.connect(lambda connection: print("Deleted", connection))

        connection_style = self.scene.style_collection.connection
        # Configure the style collection to use colors based on data types:
        connection_style.use_data_defined_colors = True

        view_nodes = FlowView(self.scene)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(view_nodes)

        ### Add nodes and layout
        logger.info(f'Loading pipeline from {pipeline_path}')
        layout = self._load_layout(self.pipeline_gui_path)
        # if the layout is None, we try to load the non-debug version before creating a new one
        if layout is None and self.resolve_macros:
            logger.info(f'Loading pipeline from {self.pipeline_gui_path_non_debug}')
            layout = self._load_layout(self.pipeline_gui_path_non_debug)

        self._add_pipeline(layout, pipeline_path)

        if layout is None:
            logger.exception('Could not load layout. Creating new.')    
            self.auto_layout()
        # self.scene.auto_arrange('graphviz_layout', prog='dot', scale=1)
        # self.scene.auto_arrange('graphviz_layout', scale=3)

    def _load_layout(self, path):
        try:
            with open(path, 'r') as f:
                layout = json.load(f)
                logger.info(f'Loaded layout from {path}')
                return layout
        except Exception:
            pass
        return None
    

    def auto_layout(self):
        # bipartite', 'circular', 'kamada_kawai', 'random',
        #                  'shell', 'spring', 'spectral'
        
        for l in ['planar_layout', 'spring_layout']:
            try:
                logger.info(f'Autolayout: trying {l}')
                self.scene.auto_arrange(l, scale=1400, align='horizontal')
                return
            except Exception as err:
                # TODO: specify exact exception and just pass
                print(err)
                pass
        logger.info(f'Autolayout: Could not apply layout. Collapsing.')

    def _remove_pl_node(self, node):
        ln_studio_node = node.model.association_to_node
        if ln_studio_node is not None:
            ln_studio_node.remove_all_inputs()





    # Collect and create Datatypes
    @staticmethod
    def port_to_key(port):
        return f"<{port.__class__.__name__}: {port.label}>"


    def _register_node(self, node_or_cls):
        if inspect.isclass(node_or_cls):
            cls_name = getattr(node_or_cls, '__name__', 'Unknown Class')
            constructor = node_or_cls
        else:
            cls_name = getattr(node_or_cls.__class__, '__name__', 'Unknown Class')
            constructor = node_or_cls.__class__
        
        # Avoid duplicate registration
        if cls_name in self.known_classes:
            return self.known_classes[cls_name]
        
        # make sure to register allowed connections
        for port in list(node_or_cls.ports_in) + list(node_or_cls.ports_out):
            new_key = self.port_to_key(port)

            if not new_key in self.known_dtypes:
                # register new datatype
                self.known_dtypes[new_key] = NodeDataType(id=new_key, name=port.label, port=port.__class__)
                

        # register node
        cls = type(cls_name, (CustomNodeDataModel,), \
            { 'name': cls_name,
            'caption': cls_name,
            'caption_visible': True,
            'num_ports': {
                PortType.input: len(node_or_cls.ports_in),
                PortType.output: len(node_or_cls.ports_out)
            },
            'data_type': {
                PortType.input: {i: self.known_dtypes[self.port_to_key(port)] for i, port in enumerate(node_or_cls.ports_in)},
                PortType.output: {i: self.known_dtypes[self.port_to_key(port)] for i, port in enumerate(node_or_cls.ports_out)}
            }
            , 'constructor': constructor
            })
        self.known_classes[cls_name] = cls
        self.registry.register_model(cls, category=getattr(node_or_cls, "category", "Unknown"))
        
        logger.info(f'Registered Node: {cls_name}')
        return cls
    
    def _create_known_classes(self, node_registry):
        ### Setup Datastructures
        # style = StyleCollection.from_json(style_json)

        self.registry = DataModelRegistry()
        # TODO: figure out how to allow multiple connections to a single input!
        # Not relevant yet, but will be when there are sync nodes (ie sync 1-x sensor nodes) etc

        if node_registry is None:
            raise Exception('Registry is Required') 

        self.known_dtypes = {}

        for node_cls in node_registry.nodes.values():
            self._register_node(node_cls)
            # self._register_node(node(**node.example_init))

    @staticmethod
    def _load_compact_yml(path):
        if os.stat(path).st_size == 0:
            # the pipeline was just created and no nodes were added yet
            return None
         
        with open(path, 'r') as f:
            yaml_dict = yaml.load(f, Loader=yaml.Loader)
        
        dct = {}
        for node_str, cfg in yaml_dict['Nodes'].items():
            dct[node_str] = {'settings': cfg, 'inputs': [], **Connectionist.str_to_dict(node_str)}

        for inp in yaml_dict['Inputs']:
            con = Connection.deserialize_compact(inp)
            dct[con['recv_node']]['inputs'].append(con)
        
        return dct
    
    def _load_pipeline_keep_macro(self, pipeline_path, layout_nodes):
        ### Add nodes
        dct = self._load_compact_yml(pipeline_path)
        logger.info(f'Loaded pipeline from {pipeline_path}')
        logger.info(f'Graph: {dct}')

        if dct is not None:
            reg = REGISTRY

            # 1. pass: create all nodes
            p_nodes = {}
            s_nodes = {}
            # print([str(n) for n in p_nodes])
            for name, itm in dct.items():
                # --- Create Livenodes/Pipeline Node ---   
                n = reg.nodes.get(itm['class'], **itm['settings'])
                p_nodes[name] = n

                # --- Create LN-Studio Node --- 
                # Since this ignores duplicates we can register the node class here
                # This is important for macros
                # Additionally, these new classes may not use ports that aren't already registered (which should be the case for pipelines executed by macros anyway)
                self._register_node(n)
                if name in layout_nodes:
                    # if the interface has changed in between saving the node/graph and loading it here the connection will log an error and be discarded
                    try:
                        s_nodes[name] = self.scene.restore_node(layout_nodes[self._get_serialize_name(n)])
                    except Exception as err:
                        layout_nodes.pop(self._get_serialize_name(n))
                        logger.exception(err)
                        logger.info(f'Node ({self._get_serialize_name(n)}) was removed from layout as it could not be resored.')
                        s_nodes[name] = self.scene.create_node(self.known_classes[n.__class__.__name__], pl_node=n, skip_association=True)
                else:
                    s_nodes[name] = self.scene.create_node(self.known_classes[n.__class__.__name__], pl_node=n, skip_association=True)

            # 2. pass: create all connections
            for name, itm in dct.items():
                # only add inputs, as, if we go through all nodes this automatically includes all outputs as well
                for con in itm['inputs']:
                    try:
                        _emit_node = p_nodes[con["emit_node"]]
                        _emit_port = p_nodes[con["emit_node"]].get_port_out_by_key(con['emit_port'])
                        _recv_node = p_nodes[name]
                        _recv_port = p_nodes[name].get_port_in_by_key(con['recv_port'])
                        
                        # --- Create Livenodes/Pipeline Connection ---   
                        _recv_node.add_input(emit_node = _emit_node, emit_port = _emit_port, recv_port = _recv_port)
                        
                        # --- Create LN-Studio Connection --- 
                        _emit_idx = [x.key for x in _emit_node.ports_out].index(con['emit_port'])
                        _recv_idx = [x.key for x in _recv_node.ports_in].index(con['recv_port'])
                        n_out = s_nodes[con["emit_node"]][PortType.output][_emit_idx]
                        n_in = s_nodes[name][PortType.input][_recv_idx]
                        self.scene.create_connection(n_out, n_in)
                    except Exception as err:
                        logger.exception(err)
                        
            # 3. pass: connect gui nodes to pipeline nodes
            # this should be done after step 2 as otherwise the connections will be created twice
            for name, itm in dct.items():
                s_nodes[name]._model.set_node_association(p_nodes[name])
                s_nodes[name]._model.set_flow_scene(self.scene)

                # COMMENT: ouch, this feels very wrong...
                s_nodes[name]._graphics_obj = attatch_click_cb(
                    s_nodes[name]._graphics_obj,
                    partial(self.node_selected.emit, p_nodes[name]))
                    # partial(self.view_configure.set_pl_node, n))

    def _load_pipeline_resolve_macro(self, pipeline_path, layout_nodes):
        ### Add nodes
        pipeline = Node.load(pipeline_path)
        if hasattr(pipeline, 'get_non_macro_node'):
            pipeline = pipeline.get_non_macro_node()

        logger.info(f'Loaded pipeline from {pipeline_path}')

        if pipeline is not None:
            ### Add nodes
            p_nodes = [(str(n), n) for n in pipeline.discover_graph(pipeline)]
            logger.info(f'Graph: {p_nodes}')
            # first pass: create all nodes
            s_nodes = {}
            # print([str(n) for n in p_nodes])
            for name, n in p_nodes:
                if self._get_serialize_name(n) in layout_nodes:
                    # lets' hope the interface hasn't changed in between
                    # TODO: actually check if it has
                    try:
                        s_nodes[name] = self.scene.restore_node(layout_nodes[self._get_serialize_name(n)])
                    except Exception as err:
                        layout_nodes.pop(self._get_serialize_name(n))
                        logger.exception(err)
                        logger.info(f'Node ({self._get_serialize_name(n)}) was removed from layout as it could not be resored.')
                        s_nodes[name] = self.scene.create_node(self.known_classes[n.__class__.__name__], pl_node=n, skip_association=True)
                else:
                    s_nodes[name] = self.scene.create_node(
                        self.known_classes[n.__class__.__name__], pl_node=n, skip_association=True)

            # second pass: create all connectins
            for name, n in p_nodes:
                # node_output refers to the node in which n is inputing data, ie n's output
                # for node_output, output_id, emit_port, recv_port in n.output_classes:
                for con in n.output_connections:
                    # print('=====')
                    out_idx = list(n.ports_out).index(con._emit_port)
                    in_idx = list(con._recv_node.ports_in).index(con._recv_port)
                    # print(out_idx, in_idx)
                    n_out = s_nodes[name][PortType.output][out_idx]
                    n_in = s_nodes[str(con._recv_node)][PortType.input][in_idx]
                    try:
                        self.scene.create_connection(n_out, n_in)
                    except ConnectionDataTypeFailure:
                        logger.exception("ERROR ConnectionDataTypeFailure: Could not connect nodes, please check.", n_out, n_in, con)
                    except MultipleInputConnectionError as err:
                        logger.exception(err)

            # third pass: connect gui nodes to pipeline nodes
            # TODO: this is kinda a hack so that we do not create connections twice (see custom model above)
            for name, n in p_nodes:
                s_nodes[name]._model.set_node_association(n)
                s_nodes[name]._model.set_flow_scene(self.scene)

                # COMMENT: ouch, this feels very wrong...
                s_nodes[name]._graphics_obj = attatch_click_cb(
                    s_nodes[name]._graphics_obj,
                    partial(self.node_selected.emit, n))
                    # partial(self.view_configure.set_pl_node, n))


    def _add_pipeline(self, layout, pipeline_path):
        # TODO: implement the switch from getting a pipeline here, to getting the path
        # -> this is done to avoid the difference between visual representation and running graph of a pipeline (e.g. with macros, where the macro node should be shown and the loaded nodes not, vs running where the macro node should not be present, but only the sub-graph nodes)
        ### Reformat Layout for easier use

        # also collect x and y min for repositioning
        layout_nodes = {}
        if layout is not None:
            min_x, min_y = 2**15, 2**15
            # first pass, collect mins and add to dict for quicker lookup
            for l_node in layout['nodes']:
                if not l_node['model']['association_to_node'] in layout_nodes:
                    layout_nodes[l_node['model']['association_to_node']] = l_node
                    min_x = min(min_x, l_node["position"]['x'])
                    min_y = min(min_y, l_node["position"]['y'])
                else:
                    logger.error(f'Duplicate node in layout: {l_node["model"]["association_to_node"]}')

            min_x, min_y = min_x - 50, min_y - 50

            # second pass, update x and y
            for l_node in layout['nodes']:
                l_node["position"]['x'] = l_node["position"]['x'] - min_x
                l_node["position"]['y'] = l_node["position"]['y'] - min_y

        if self.resolve_macros:
            self._load_pipeline_resolve_macro(pipeline_path, layout_nodes)
        else:
            self._load_pipeline_keep_macro(pipeline_path, layout_nodes)

        print('Added pipeline')

    def _find_initial_pl(self, pl_nodes):
        # initial node: assume the first node we come across, that doesn't have any inputs is our initial node
        # TODO: this will lead to problems further down
        # when we implement piplines as nodes, there might not be nodes without inputs, then we need to take any node and make sure the discover all etc work
        # maybe also consider adding a warning if there are graphs that are not connected ie and which one will be saved...
        initial_pl_nodes = [
            n for n in pl_nodes
            if len(n.ports_in) == 0 and len(n.output_connections) > 0
        ]

        # if we cannot find a node without inputs, take the first that has outputs
        if len(initial_pl_nodes) == 0:
            initial_pl_nodes = [
                n for n in pl_nodes if len(n.output_connections) > 0
            ]
      
        # if this is still empty, take any existing node
        if len(initial_pl_nodes) == 0:
            initial_pl_nodes = pl_nodes

        return initial_pl_nodes[0]
    
    @staticmethod
    def _get_serialize_name(node):
        name = str(node)
        if hasattr(node, '_serialize_name'):
            name = node._serialize_name()

        if hasattr(node, "get_name_resolve_macro"):
            return name.replace(node.name, node.get_name_resolve_macro())
        else:
            return name
    
    def get_state(self):
        state = self.scene.__getstate__()
        vis_state = {'connections': state['connections'], 'nodes': []}
        pl_nodes = []
        for val in state['nodes']:
            if 'association_to_node' in val['model']:
                _n = val['model']['association_to_node']
                pl_nodes.append(_n)
                val['model']['association_to_node'] = self._get_serialize_name(_n)
            vis_state['nodes'].append(val)

        return vis_state, self._find_initial_pl(pl_nodes)

    def save(self):
        vis_state, pipeline = self.get_state()
        logger.debug(f'initial node used for saving: {str(pipeline)}')

        with open(self.pipeline_gui_path, 'w') as f:
            json.dump(vis_state, f, indent=2)
        
        # TODO: try to clone / save and load the whole thing to check if the gui allowed configs, that we cannot load afterwards...
        # Node.load(self.pipeline_path)

        # loadable file format
        pipeline_base = self.pipeline_path.replace('.yml', '', 1)
        if not self.read_only:
            pipeline.save(pipeline_base, extension='yml')

        try:
            pipeline.dot_graph_full(transparent_bg=True, edge_labels=False, filename=pipeline_base, file_type='png')
            pipeline.dot_graph_full(transparent_bg=True, filename=pipeline_base, file_type='pdf')
        except graphviz.backend.execute.ExecutableNotFound as err:
            logger.exception('Could not create dot graph. Executable not found.')

    
    def stop(self):
        _, pipeline = self.get_state()
        nodes = pipeline.discover_graph(pipeline)
        for node in pipeline.discover_graph(pipeline):
            try:
                logger.info(f'Stopping in case they created ressources on __init__. Node: {node}')
                node.stop()
            except Exception as e:
                logger.exception(e)


