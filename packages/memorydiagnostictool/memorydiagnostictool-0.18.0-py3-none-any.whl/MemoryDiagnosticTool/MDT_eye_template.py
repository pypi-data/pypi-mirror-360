import json
import os
import re
from collections import defaultdict

        
def html_eye_plot(mdt_eye_html, eye_data, mode, delaycenter=[], vrefcenter=[]):
    try:
        
        if mode == 'qcs':
            Params = "QCS"
        elif mode == 'qca':
            Params = "QCA"
        elif mode == 'dcs':
            Params = "DCS"
        elif mode == 'readeven':
            Params = "ReadEven"
        elif mode == 'readodd':
            Params = "ReadOdd"
        elif mode == 'readscan':
            Params = "ReadScan"
        elif mode == 'write':
            Params = "Write"
        else:
            Params = ""

        canvas=''
        dataset=''
        datasets =''
        configs =''
        charts =''
        #insert center data into eye data
        center={}
        try:
            if delaycenter and vrefcenter:
                if mode == 'qcs':
                    for key, value in delaycenter.items():
                        if key in vrefcenter:
                            vref= vrefcenter[key]
                            new_key = (key[0],key[1],key[2],key[3],key[4])
                            if new_key in eye_data:
                                center[new_key] = [[value, vref]]          
                elif mode == 'qca' or mode=='dcs':
                    for key, value in delaycenter.items():
                        if key in eye_data:
                            if key in vrefcenter:                             
                                vref= vrefcenter[key]
                                # just for plotting center purpose, as dcs starts by adding 1tck
                                if mode == 'dcs':
                                    x0, y0 = eye_data[key][0]
                                    if x0 > value:
                                        value += 64
                                center[key] = [[value, vref]] 
                elif mode == 'readeven' or mode == 'readodd' or mode == 'readscan':
                    for key, value in delaycenter.items():
                        if key in eye_data:
                            if key in vrefcenter:
                                vref= vrefcenter[key]
                                center[key] = [[value, vref]]
                elif mode == 'write':
                   for key, value in delaycenter.items():
                        (_soc, _iod, _ch, _sub, _rank, _bit) = key
                        nibble = _bit//4
                        vref_key = (_soc, _iod, _ch, _sub, _rank, nibble)
                        if key in eye_data:
                            if vref_key in vrefcenter:
                                vref= vrefcenter[vref_key]
                                center[key] = [[value, vref]]
        except:
            print("no center been added")
        
        if mode == 'qcs' or mode=='dcs':
            new_eye_data = defaultdict(lambda: [[{}]] * 2)
            for (_soc, _iod, _ch, _sub, _rank), value in eye_data.items():
                key = (_soc, _iod, _ch, _sub, _rank)
                # Reformat [x, y] -> {"x": x, "y": y}
                formatted_value = [{"x": x, "y": y} for x, y in value]
                # Assign each bit's formatted list to the correct position
                new_eye_data[key][0] = formatted_value
                if key in center:
                    formatted_value = [{"x": x, "y": y} for x, y in center[_soc, _iod, _ch, _sub, _rank]]
                    new_eye_data[key][1] = formatted_value

        elif mode == 'qca':
            new_eye_data = defaultdict(lambda: [[{}]] * 20)
            
            for (_soc, _iod, _ch, _sub, _rank, _dev), value in eye_data.items():
                new_key = (_soc, _iod, _ch, _sub, _rank)
                # Reformat [x, y] -> {"x": x, "y": y}
                formatted_value = [{"x": x, "y": y} for x, y in value]
                # Assign each bit's formatted list to the correct position
                new_eye_data[new_key][_dev] = formatted_value 
                # Reformat and assign center data
                key = (_soc, _iod, _ch, _sub, _rank, _dev)
                if key in center:
                    formatted_value = [{"x": x, "y": y} for x, y in center[_soc, _iod, _ch, _sub, _rank, _dev]]
                    new_eye_data[new_key][_dev+10] = formatted_value
        else:            
            new_eye_data = defaultdict(lambda: [[{}]] * 16)
            
            for (_soc, _iod, _ch, _sub, _rank, _bit), value in eye_data.items():
                db = _bit // 8  # Group bits into dbs: bits 0–7 → db 0, bits 8–15 → db 1, etc.
                db_bit = _bit % 8  # Position within db group
                new_key = (_soc, _iod, _ch, _sub, _rank, db)
                # Reformat [x, y] -> {"x": x, "y": y}
                formatted_value = [{"x": x, "y": y} for x, y in value]
                # Assign each bit's formatted list to the correct position
                new_eye_data[new_key][db_bit] = formatted_value 
                # Reformat and assign center data
                key = (_soc, _iod, _ch, _sub, _rank, _bit)
                if key in center:
                    formatted_value = [{"x": x, "y": y} for x, y in center[_soc, _iod, _ch, _sub, _rank, _bit]]
                    new_eye_data[new_key][db_bit+8] = formatted_value

        #set up all the 
        for _soc in range(2):
            for _iod in range(2):
                for _ch in range(8):
                    for _sub in range(2):
                        for _rank in range(2):                           
                            if mode == 'qcs' or mode == 'qca' or mode=='dcs':
                                key = _soc, _iod, _ch, _sub, _rank
                                if key in new_eye_data:
                                    value = new_eye_data[key]
                                else:
                                    value = []
                                var_name = f"{Params}_Soc{_soc}_Iod{_iod}_Ch{_ch}_Phy{_sub}_Cs{_rank}"

                                Ch = _ch
                                Phy= _sub
                                Cs = _rank
                                dataset +=f"""
                                const {var_name} = {value};
                                """
                                if (int(_rank)==0):
                                    canvas += f"""	
                                    <div id="Graph_Soc{_soc}_Iod{_iod}_Ch{Ch}_Phy{Phy}" class="graph-container">
                                        <h3>Soc{_soc}_Iod{_iod}_Ch{Ch}_Phy{Phy}</h3>"""    
                                canvas += f"""
                                        <p class="graph-caption">Rank{Cs}</p>
                                        <canvas id="canvas_{var_name}" width="400" height="200"></canvas>
                                        """   
                                if (int(_rank)==1):
                                    canvas += f"""
                                    </div>
                                    """
                                datasets +=f"""
                                const datasets_{var_name} = pointStyles.map((style, i) => ({{
                                  label: labels[i],
                                  data: {var_name}[i],
                                  pointStyle: style,
                                  borderColor: colors[i],
                                  backgroundColor: colors[i],
                                  pointRadius: sizes[i],
                                  pointHoverRadius: 2,
                                  showLine: false
                                }}));
                                """
                                configs +=f"""
                                const config_{var_name} = createScatterConfig(datasets_{var_name})
                                
                                """
                                charts+= f"""
                                new Chart(document.getElementById('canvas_{var_name}'), config_{var_name});
                                """
                          
                            else:
                                for _db in range(5):
                                    key = _soc, _iod, _ch, _sub, _rank, _db
                                    if key in new_eye_data:
                                        value = new_eye_data[key]
                                    else:
                                        value = []
                                    var_name = f"{Params}_Soc{_soc}_Iod{_iod}_Ch{_ch}_Phy{_sub}_Cs{_rank}_Db{_db}"

                                    Ch = _ch
                                    Phy= _sub
                                    Cs = _rank
                                    Db = _db
                                    dataset +=f"""
                                    const {var_name} = {value};
                                    """
                                    if (int(Db)==0):
                                        canvas += f"""	
                                        <div id="Graph_Soc{_soc}_Iod{_iod}_Ch{Ch}_Phy{Phy}_Cs{Cs}" class="graph-container">
                                            <h3>Soc{_soc}_Iod{_iod}_Ch{Ch}_Phy{Phy}_Cs{Cs}</h3>"""    
                                    canvas += f"""
                                            <p class="graph-caption">Db{Db}</p>
                                            <canvas id="canvas_{var_name}" width="400" height="200"></canvas>
                                            """   
                                    if (int(Db)==4):
                                        canvas += f"""
                                        </div>
                                        """
                                    datasets +=f"""
                                    const datasets_{var_name} = pointStyles.map((style, i) => ({{
                                      label: labels[i],
                                      data: {var_name}[i],
                                      pointStyle: style,
                                      borderColor: colors[i],
                                      backgroundColor: colors[i],
                                      pointRadius: sizes[i],
                                      pointHoverRadius: 2,
                                      showLine: false
                                    }}));
                                    """
                                    configs +=f"""
                                    const config_{var_name} = createScatterConfig(datasets_{var_name});
                                    
                                    """
                                    charts+= f"""
                                    new Chart(document.getElementById('canvas_{var_name}'), config_{var_name});
                                    """

        if mode == 'qcs' or mode=='dcs':
            html_template = f"""       <!-- f-string starts here -->
            
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <title>{Params} Eye Plot </title>
              <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    h1 {{
                        text-align: center;
                        color: #333;
                    }}
                     /* Set the size of the graphs */
                    .graph-container {{
                        display: flex; /* Enables Flexbox */
                        justify-content: space-evenly; /* Distribute canvases evenly with space in between */
                        width: 60%;  /* Reducing the width of the graph to 50% */
                        height: 200px; /* Adjusting the height of the graph */
                        margin-bottom: 60px; /* Adding space between graph sections */
                        margin-top: 60px; /* Adding space between graph sections */
                    }}
                    .graph-caption {{
                        text-align: center-left;
                        font-size: 14px;
                        color: #555;
                        margin-top: 100px;
                        margin-right: 10px;
                    }}	
            </style>	                      
            </head>
            <body>
              <h1> {Params} Eye Plot </h1>
              {canvas}

              <script>
                {dataset}

                const labels = ['CS', 'center'];
                
                const pointStyles = [
                  'circle', 'circle'
                ];

                const colors = [
                  'orange', 'orange'
                ];
                
                const sizes = [
                  2, 4
                ];

                {datasets}
                    const createScatterConfig = (datasets) => ({{
                      type: 'scatter',
                      data: {{ datasets }},
                      options: {{
                        plugins: {{
                          legend: {{
                            labels: {{
                              usePointStyle: true,
                              pointStyleWidth: 15
                            }}
                          }}
                        }},
                        animation: false,
                        scales: {{
                          x: {{
                            type: 'linear',
                            position: 'bottom'
                          }}
                        }}
                      }}
                    }});    
                
                {configs}

                {charts}

              </script>
            </body>
            </html>
            """
        elif mode == 'qca':
            html_template = f"""       <!-- f-string starts here -->
            
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <title>{Params} Eye Plot </title>
              <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    h1 {{
                        text-align: center;
                        color: #333;
                    }}
                     /* Set the size of the graphs */
                    .graph-container {{
                        display: flex; /* Enables Flexbox */
                        justify-content: space-evenly; /* Distribute canvases evenly with space in between */
                        width: 60%;  /* Reducing the width of the graph to 50% */
                        height: 200px; /* Adjusting the height of the graph */
                        margin-bottom: 60px; /* Adding space between graph sections */
                        margin-top: 60px; /* Adding space between graph sections */
                    }}
                    .graph-caption {{
                        text-align: center-left;
                        font-size: 14px;
                        color: #555;
                        margin-top: 100px;
                        margin-right: 10px;
                    }}	
            </style>	                      
            </head>
            <body>
              <h1> {Params} Eye Plot </h1>
              {canvas}

              <script>
                 {dataset}

                const labels = ['Dev0', 'Dev1', 'Dev2', 'Dev3', 'Dev4', 'Dev5', 'Dev6', 'Dev7', 'Dev8', 'Dev9',
                                'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9'];
                
                const pointStyles = [
                  'circle', 'cross', 'crossRot', 'star', 'triangle',
                  'rect', 'rectRounded', 'rectRot', 'cirle', 'rect',
                  'circle', 'cross', 'crossRot', 'star', 'triangle',
                  'rect', 'rectRounded', 'rectRot', 'cirle', 'rect'
                ];

                const colors = [
                  'red', 'orange', 'darkyellow', 'green', 'blue',
                  'purple', 'pink', 'brown', 'lightblue', 'lightgreen',
                  'red', 'orange', 'darkyellow', 'green', 'blue',
                  'purple', 'pink', 'brown', 'lightblue', 'lightgreen'
                ];
                
                const sizes = [
                  2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                  4, 4, 4, 4, 4, 4, 4, 4, 4, 4
                ];

                {datasets}
                    const createScatterConfig = (datasets) => ({{
                      type: 'scatter',
                      data: {{ datasets }},
                      options: {{
                        plugins: {{
                          legend: {{
                            labels: {{
                              usePointStyle: true,
                              pointStyleWidth: 15
                            }}
                          }}
                        }},
                        animation: false,
                        scales: {{
                          x: {{
                            type: 'linear',
                            position: 'bottom'
                          }}
                        }}
                      }}
                    }});    
                
                {configs}

                {charts}

              </script>
            </body>
            </html>
            """

        else:
            html_template = f"""       <!-- f-string starts here -->
            
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <title>{Params} Eye Plot </title>
              <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    h1 {{
                        text-align: center;
                        color: #333;
                    }}
                     /* Set the size of the graphs */
                    .graph-container {{
                        display: flex; /* Enables Flexbox */
                        justify-content: space-evenly; /* Distribute canvases evenly with space in between */
                        width: 60%;  /* Reducing the width of the graph to 50% */
                        height: 200px; /* Adjusting the height of the graph */
                        margin-bottom: 60px; /* Adding space between graph sections */
                        margin-top: 60px; /* Adding space between graph sections */
                    }}
                    .graph-caption {{
                        text-align: center-left;
                        font-size: 14px;
                        color: #555;
                        margin-top: 100px;
                        margin-right: 10px;
                    }}	
            </style>	                      
            </head>
            <body>
              <h1> {Params} Eye Plot </h1>
              {canvas}

              <script>
                 {dataset}

                const labels = ['DQ0', 'DQ1', 'DQ2', 'DQ3', 'DQ4', 'DQ5', 'DQ6', 'DQ7',
                                'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7'];
                
                const pointStyles = [
                  'circle', 'cross', 'crossRot', 'star', 'triangle',
                  'rect', 'rectRounded', 'rectRot',
                  'circle', 'cross', 'crossRot', 'star', 'triangle',
                  'rect', 'rectRounded', 'rectRot'
                ];

                const colors = [
                  'red', 'orange', 'darkyellow', 'green', 'blue',
                  'purple', 'pink', 'brown',
                  'red', 'orange', 'darkyellow', 'green', 'blue',
                  'purple', 'pink', 'brown'
                ];
                
                const sizes = [
                  2, 2, 2, 2, 2, 2, 2, 2,
                  4, 4, 4, 4, 4, 4, 4, 4
                ];

                {datasets}
                    const createScatterConfig = (datasets) => ({{
                      type: 'scatter',
                      data: {{ datasets }},
                      options: {{
                        plugins: {{
                          legend: {{
                            labels: {{
                              usePointStyle: true,
                              pointStyleWidth: 15
                            }}
                          }}
                        }},
                        animation: false,
                        scales: {{
                          x: {{
                            type: 'linear',
                            position: 'bottom'
                          }}
                        }}
                      }}
                    }});    
                
                {configs}

                {charts}

              </script>
            </body>
            </html>
            """


        with open(mdt_eye_html, 'w') as f:
            f.write(html_template)

    except:
        print(f"Fail to generate {mode} eye")