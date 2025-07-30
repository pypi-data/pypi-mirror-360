// script.js
document.addEventListener('DOMContentLoaded', () => {
    //////////////////////////////////////////
    // Configuration for each node baseType //
    //////////////////////////////////////////
    const nodeDefs = {
      pump: {
        options: ['TecanXCPump','JKemPump','TecanCentrisPump','TecanXLPPump','RunzePump','LongerPeristalticPump'],
        settings: [
          { key:'com_port',    label:'COM Port',    type:'string', default:'' },
          { key:'address',     label:'Address',     type:'int',    default:0 },
          { key:'syringe_volume',label:'Syringe Volume (mL)', type:'float', default:0,    toL:true },
          { key:'num_valve_port',label:'# Valve Ports', type:'int', default:0 },
          { key:'init_valve',  label:'Init Valve',  type:'int',    default:null },
          { key:'out_valve',   label:'Out Valve',   type:'int',    default:null },
          { key:'home_pos',    label:'Home Position', type: 'int', default:null }
        ]
      },
      valve: {
        options: ['JKem4in1Valve','ValcoSelectionValve','JKemNewValve','RunzeSelectionValve'],
        settings: [
          { key:'com_port', label:'COM Port', type:'string', default:'' },
          { key:'address',  label:'Address',  type:'int',    default:0 },
          { key:'num_port', label:'# Ports',  type:'int',    default:0 }
        ]
      },
      hotplate: {
        options: ['HeidolphHotplate','IKAHotplate'],
        settings: [
          { key:'com_port', label:'COM Port', type:'string', default:'' },
          { key:'max_temp', label:'Max Temp', type:'float',  default:0 },
          { key:'max_rpm',  label:'Max RPM',  type:'int',    default:0 }
        ]
      },
      relay: {
        options: ['R421B16Relay','JYdaqRelay','CE221ARelay'],
        settings: [
          { key:'com_port', label:'COM Port', type:'string', default:'' },
          { key:'address',  label:'Address',  type:'int',    default:0 },
          { key:'channel',  label:'Channel',  type:'int',    default:0 }
        ]
      },
      serial_device: {
        options: ['SerialDevice'],
        settings: [
          { key:'com_port', label:'COM Port', type:'string', default:'' },
          { key:'address',  label:'Address',  type:'int',    default:0 },
        ]        
      },
      vessel: {
        options: ['Vessel'],
        settings: [
          { key:'max_volume',    label:'Max Volume',    type:'float', default:0 },
          { key:'current_volume',label:'Current Volume',type:'float', default:0 },
          { key:'addable',       label:'Addable',       type:'bool',  default:true },
          { key:'removable',     label:'Removable',     type:'bool',  default:true },
          { key:'content',       label:'Content',       type:'string',default:'' }
        ]
      }
    };
  
    //////////////////////
    // global counters //
    //////////////////////
    const ctr = { pump:0, valve:0, hotplate:0, relay:0, vessel:0 };
  
    /////////////////////
    // undo history    //
    /////////////////////
    let history = [], histIdx = -1;
    function pushHistory() {
      // prune redo
      history = history.slice(0, histIdx+1);
      history.push(cy.json());
      histIdx++;
    }
    function undo() {
      if (histIdx > 0) {
        histIdx--;
        cy.json(history[histIdx]);
      }
    }
  
    /////////////////////////
    // cytoscape instance  //
    /////////////////////////
    const cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
          {
            selector: 'node',
            style: {
              'label': 'data(name)',
              'text-valign': 'bottom',
              'text-halign': 'center',
              'background-image': 'data(image)',
              'background-fit': 'cover',
              'width': 60,
              'height': 60,
              'border-width': 1,
              'border-color': '#000'
            }
          },
        { selector:'edge', style:{
            'width':3,'curve-style':'bezier','target-arrow-shape':'triangle'
        }},
        { selector:'edge[type="volumetric"]', style:{
            'line-color':'#00008B','target-arrow-color':'#00008B'
        }},
        { selector:'edge[type="gas"]', style:{
            'line-color':'#D3D3D3','target-arrow-color':'#D3D3D3'
        }},
        { selector:'edge[type="thermal"]', style:{
            'line-color':'#FF0000','target-arrow-color':'#FF0000'
        }}
      ],
      layout: { name:'preset' },
      elements: []
    });
    cy.on('dbltap', 'node', evt => {
        openNodeModal(evt.target);
      });

    ////////////////////////
    // initial default    //
    ////////////////////////
    function loadTemplate(template) {
      // Clear existing elements
      cy.elements().remove();
      
      // Create nodes
      template.nodes.forEach(node => {
          const baseType = Object.keys(nodeDefs).find(bt => 
              nodeDefs[bt].options.includes(node.type)
          );
          
          if (baseType) {
              addNode(baseType, node.position, {
                  data: {
                      name: node.name,
                      type: node.type
                  },
                  settings: node.settings
              });
          }
      });
      
      // Create edges
      template.links.forEach(link => {
          const srcNode = cy.nodes().filter(n => n.data('name') === link.source);
          const tgtNode = cy.nodes().filter(n => n.data('name') === link.target);
          
          if (srcNode.length && tgtNode.length) {
              addEdge(srcNode, tgtNode, link.type, link.source_port || 0);
          }
      });
    }
    function initDefault() {
      // default Pump
    const p = addNode('pump', { x:100, y:100 });
    // two vessels with fixed names, no initial links
    const v1 = addNode('vessel', { x:300, y:50 }, {
        data:    { name: 'Gas Reservoir Vessel' },
        settings:{ max_volume:1e6, current_volume:1e6, addable:false, removable:true }
    });
    const v2 = addNode('vessel', { x:300, y:150 }, {
        data:    { name: 'Waste Vessel' },
        settings:{ max_volume:1000, current_volume:0, addable:true, removable:false }
    });
    }
    // initDefault();

    fetch('/template')
        .then(response => response.json())
        .then(template => {
            if (template.nodes && template.nodes.length > 0) {
                loadTemplate(template);
            } else {
                initDefault();
            }
            pushHistory();
        })
        .catch(error => {
            console.error('Error loading template:', error);
            initDefault();
            pushHistory();
        });

    // pushHistory();
  
  
    //////////////////////
    // dragging sidebar //
    //////////////////////
    document.querySelectorAll('#sidebar .draggable').forEach(el => {
        el.addEventListener('dragstart', e => {
      -   e.dataTransfer.setData('text/plain', e.target.dataset.type);
        });
      });
    // use the actual cytoscape container (canvas) for drop events:
    const cyContainer = cy.container();  // → this is the actual <canvas> element
    cyContainer.addEventListener('dragover', e => {
    e.preventDefault();
    // tell the browser we intend to copy (allows drop)
    e.dataTransfer.dropEffect = 'copy';
    });

    cyContainer.addEventListener('drop', e => {
    e.preventDefault();
    // read from the same mime you set in dragstart
    const baseType =
        e.dataTransfer.getData('application/node-type') ||
        e.dataTransfer.getData('text/plain');
    if (!baseType) return;

    const rect = cyContainer.getBoundingClientRect();
    const zoom = cy.zoom(), pan = cy.pan();
    const x = (e.clientX - rect.left  - pan.x)/zoom;
    const y = (e.clientY - rect.top   - pan.y)/zoom;

    addNode(baseType, { x, y });
    pushHistory();
    });
  
    ///////////////////////////////////////////////////
    // sequential clicks to create an edge (two taps)//
    ///////////////////////////////////////////////////
    let edgeSource = null;
    cy.on('tap', 'node', evt => {
      const n = evt.target;
      if (!edgeSource) {
        edgeSource = n;
        n.select();
      } else {
        if (n !== edgeSource) {
          const aType = edgeSource.data('baseType');
          const bType = n.data('baseType');

          if (aType === 'hotplate' || bType === 'hotplate') {
            // identify hotplate and the other node
            const hotplateNode = (aType === 'hotplate' ? edgeSource : n);
            const otherNode    = (hotplateNode === edgeSource ? n : edgeSource);

            // only allow vessel on the other end
            if (otherNode.data('baseType') !== 'vessel') {
              alert('A Hotplate can only connect to a Vessel.');
            } else {
              addEdge(hotplateNode, otherNode, 'thermal', 0);
              pushHistory();
            }
          }

          else {
            const needsPort = ['pump','valve'].includes(edgeSource.data('baseType'));
            if (needsPort) {
              // Pumps & valves may need a source port, so show the edge‑creation modal
              openEdgeModal(edgeSource, n);
            } else {
              // For everything else, just drop in a default volumetric edge
              addEdge(edgeSource, n, 'volumetric', 0);
              pushHistory();
            }
          }
          
        }
        edgeSource.unselect();
        edgeSource = null;
      }
    });
  
  
    ////////////////////////////////
    // top-bar buttons & shortcuts//
    ////////////////////////////////
    document.getElementById('copyBtn').onclick   = copySelection;
    document.getElementById('pasteBtn').onclick  = pasteClipboard;
    document.getElementById('deleteBtn').onclick = deleteSelection;
    document.getElementById('saveBtn').onclick   = saveTemp;
    document.getElementById('undoBtn').onclick   = undo;
    document.getElementById('exportBtn').onclick = exportGraph;
    document.getElementById('exitBtn').onclick = exitDesigner;
  
    window.addEventListener('keydown', e=>{
      if (e.ctrlKey && e.key==='c') { e.preventDefault(); copySelection(); }
      if (e.ctrlKey && e.key==='v') { e.preventDefault(); pasteClipboard(); }
      if (e.key==='Delete')     { e.preventDefault(); deleteSelection(); }
      if (e.ctrlKey && e.key==='s') { e.preventDefault(); saveTemp(); }
      if (e.ctrlKey && e.key==='z') { e.preventDefault(); undo(); }
    });
  
    /////////////////////////////////
    // copy / paste implementation //
    /////////////////////////////////
    let clipboard = { nodes:[], edges:[] };
    function copySelection(){
      const sel = cy.$(':selected');
      // copy nodes
      clipboard.nodes = sel.nodes().map(n=>({
        data: {...n.data()},
        position: {...n.position()}
      }));
      // copy edges only between selected nodes
      clipboard.edges = sel.edges().filter(e=>{
        const s = e.data('source'), t = e.data('target');
        return clipboard.nodes.find(n=>n.data.id===s) && clipboard.nodes.find(n=>n.data.id===t);
      }).map(e=>({...e.data()}));
      alert('Copied '+clipboard.nodes.length+' nodes, '+clipboard.edges.length+' edges');
    }
    function pasteClipboard(){
      if (!clipboard.nodes.length) return;
      const idMap = {};
      // paste nodes
      clipboard.nodes.forEach(orig=>{
        const b = orig.data.baseType;
        const p = { x: orig.position.x+20, y: orig.position.y+20 };
        const n = addNode(b, p, { data:orig.data }); // uses orig settings & type & name
        idMap[ orig.data.id ] = n.id();
      });
      // paste edges
      clipboard.edges.forEach(ed=>{
        const sid = idMap[ed.source], tid = idMap[ed.target];
        if (sid && tid) addEdge(cy.getElementById(sid), cy.getElementById(tid), ed.type, ed.source_port || 0);
      });
      pushHistory();
    }
  
    ///////////////////////
    // delete selection  //
    ///////////////////////
    function deleteSelection(){
      const sel = cy.$(':selected');
      if (sel.length>0){
        cy.remove(sel);
        pushHistory();
      }
    }
  
    ///////////////////////////
    // save to localStorage  //
    ///////////////////////////
    function saveTemp(){
      localStorage.setItem('fluidicGraph', JSON.stringify(exportData(),null,2));
      alert('Graph saved locally');
    }
  
    ///////////////////////////
    // export JSON to file   //
    ///////////////////////////
    function exportGraph(){
      const payload = exportData();
      const defaultName = 'fluidic_design.json';
      const fname = prompt('Enter export file name (no path necessary):', defaultName);
      if (fname === null) return; // cancelled

      // Create a JSON blob and let the browser handle the Save As dialog
      const blob = new Blob([JSON.stringify(payload, null, 2)], {type: 'application/json'});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = fname.endsWith('.json') ? fname : fname + '.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(a.href);
      alert('Design exported successfully');
    }

    /////////////////////////////
    //           exit          //
    /////////////////////////////
    function exitDesigner() {
      fetch('/exit', { method: 'POST' })
          .then(() => {
              alert('Designer closed. You may close this browser tab.');
          })
          .catch(error => {
              console.error('Exit error:', error);
              alert('Error exiting designer');
          });
    }
      
    /////////////////////////////
    // assemble export payload //
    /////////////////////////////
    function exportData(){
      const nodes = cy.nodes().map(n=>{
        // clone & clean settings
        const raw = n.data('settings') || {};
        const settings = Object.fromEntries(
          Object.entries(raw).filter(([ , v ]) => v !== null)
        );
        return {
          type:    n.data('type'),
          name:    n.data('name'),
          ...(Object.keys(settings).length ? { settings } : {}) 
          // settings:n.data('settings')
        };
      });
      const links = cy.edges().map(e=>{
        const d = e.data();
        return {
          type:        d.type,
          source:      cy.getElementById(d.source).data('name'),
          source_port: d.source_port || 0,
          target:      cy.getElementById(d.target).data('name')
        };
      });
      return { nodes, links };
    }
  
  
    ///////////////////////////////////
    // add a node helper function   //
    ///////////////////////////////////
    function addNode(baseType, pos, extras = {}) {
        ctr[baseType]++;
        const id   = baseType + '_' + Date.now() + '_' + ctr[baseType];
        const def  = nodeDefs[baseType];
        const type = extras.data?.type || def.options[0];
    
        // build settings…
        const settings = {};
        def.settings.forEach(f => {
          settings[f.key] = extras.settings?.[f.key] ?? f.default;
        });
    
        // default name…
        const name = extras.data?.name
                   || baseType.charAt(0).toUpperCase() + baseType.slice(1)
                   + (ctr[baseType] > 1 ? ctr[baseType] : '');
    
        // **here we set the `image` field** to point at the right SVG:
        const image = `icons/${baseType}.svg`;
    
        return cy.add({
          group: 'nodes',
          data: { id, baseType, type, name, settings, image },
          position: pos
        });
      }
  
    //////////////////////////////////////
    // add an edge helper function      //
    //////////////////////////////////////
    function addEdge(srcNode, tgtNode, type, port=0){
      const id = 'e_'+Date.now()+'_'+Math.floor(Math.random()*10000);
      cy.add({
        group:'edges',
        data:{ id, source: srcNode.id(), target: tgtNode.id(), type, source_port:port }
      });
    }
  
  
    ///////////////////////////
    // Node-edit modal logic //
    ///////////////////////////
    const nodeModal = document.getElementById('nodeModal'),
          nodeForm  = document.getElementById('nodeForm'),
          saveNode  = document.getElementById('saveNodeBtn'),
          closeBtns = document.querySelectorAll('.modal .close');
    let activeNode = null;
  
    closeBtns.forEach(b=>b.onclick = ()=>{ nodeModal.style.display='none'; edgeModal.style.display='none'; });
  
    function openNodeModal(node){
      activeNode = node;
      nodeForm.innerHTML = '';
      const defs = nodeDefs[ node.data('baseType') ];
  
      // Name
      nodeForm.insertAdjacentHTML('beforeend', `
        <label>Name<input type="text" name="name" value="${node.data('name')}"></label>
      `);
  
      // Type
      let optHtml = defs.options.map(o=>
        `<option value="${o}"${ o===node.data('type')?' selected':'' }>${o}</option>`
      ).join('');
      nodeForm.insertAdjacentHTML('beforeend', `
        <label>Type<select name="type">${optHtml}</select></label>
      `);
  
      // Settings fields
      defs.settings.forEach(f=>{
        let val = node.data('settings')[f.key];
        if (f.toL) val = val*1e3; // convert L→mL for input
        if (f.type==='bool'){
          nodeForm.insertAdjacentHTML('beforeend', `
            <label>${f.label}
              <select name="${f.key}">
                <option value="true"${val?' selected':''}>true</option>
                <option value="false"${!val?' selected':''}>false</option>
              </select>
            </label>`);
        } 
        else if (f.type === 'string'){
            nodeForm.insertAdjacentHTML('beforeend',`
                <label>${f.label}
                <input type="text" name="${f.key}" value="${val}">
                </label>`);
        }
        else {
          nodeForm.insertAdjacentHTML('beforeend', `
            <label>${f.label}
              <input type="number" step="${f.type==='int'?1:'any'}" name="${f.key}" value="${val}">
            </label>`);
        }
      });
  
      nodeModal.style.display = 'flex';
    }
  
    saveNode.onclick = ()=>{
      const data = new FormData(nodeForm);
      // update name & type
      activeNode.data('name', data.get('name'));
      activeNode.data('type', data.get('type'));
      // update settings
      const defs = nodeDefs[ activeNode.data('baseType') ];
      const sett = {};
      defs.settings.forEach(f=>{
        let v = data.get(f.key);
        if (f.type==='int')    v = parseInt(v);
        if (f.type==='float')  v = parseFloat(v);
        if (f.toL)             v = v*1e-3;  // mL→L
        if (f.type==='bool')   v = (v==='true');
        sett[f.key] = v;
      });
      activeNode.data('settings', sett);
      nodeModal.style.display='none';
      pushHistory();
    };
  
  
    /////////////////////////////
    // Edge-create modal logic //
    /////////////////////////////
    const edgeModal = document.getElementById('edgeModal'),
          edgeForm  = document.getElementById('edgeForm'),
          edgeType  = document.getElementById('edgeType'),
          edgePort  = document.getElementById('edgePort'),
          portField = document.getElementById('portField'),
          saveEdge  = document.getElementById('saveEdgeBtn');
    let edgeSrc=null, edgeTgt=null;
  
    // show/hide port input
    edgeType.onchange = () => {
        if (
          ['volumetric','gas'].includes(edgeType.value) &&
          ['pump','valve'].includes(edgeSrc.data('baseType'))
        ) {
          portField.style.display = '';
        } else {
          portField.style.display = 'none';
        }
      };
  
    function openEdgeModal(src, tgt) {
    edgeSrc = src; edgeTgt = tgt;
    edgeType.value = 'volumetric';
    edgePort.value = 0;
    // show port input if source is pump or valve
    portField.style.display =
    (
      ['volumetric','gas'].includes(edgeType.value) &&
      ['pump','valve'].includes(edgeSrc.data('baseType'))
    )
    ? '' : 'none';
    edgeModal.style.display = 'flex';
    }
  
    saveEdge.onclick = ()=>{
      let tp = edgeType.value,
          pt = 0;
      if (portField.style.display==='') {
        pt = parseInt(edgePort.value);
        // check already used
        const used = cy.edges().filter(e=>{
          return e.data('source')===edgeSrc.id()
              && e.data('source_port')===pt;
        }).length;
        if (used) {
          alert('Port '+pt+' already used on that source');
          return;
        }
      }
      addEdge(edgeSrc, edgeTgt, tp, pt);
      edgeModal.style.display='none';
      pushHistory();
    };

    cy.on('tap', 'edge', evt => {
        const e = evt.target;
        const pt = e.data('source_port') || 0;
        alert(`Edge source_port = ${pt}`);
      });
  
  });
  