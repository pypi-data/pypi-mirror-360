

        
def parse_to_html(mdt_html, pmu_train_status, summary_table, ordered_result, missing_print, analysis_result):

    wl_rxen_seq=""
    if ordered_result:
        wl_rxen_seq= "<strong>WL to RxEN order mismatched:</strong><br>" + ordered_result
    else:
        wl_rxen_seq="<strong>No warning detected.</strong>"
    
    missing_print_summary=""
    if missing_print:
        missing_print_summary= missing_print
    else:
        missing_print_summary="<strong>No missing print detected.</strong>"
    html_template = """
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Line Graph and Table Toggle Example</title>
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f9;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .section {
            background-color: #fff;
            border: 1px solid #ddd;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
        }
        .section h2 {
            color: #007BFF;
        }
        .content {
            font-size: 16px;
            color: #333;
        }
        .error-state {
            background-color: #f8d7da;
            border-left: 6px solid #f5c6cb;
        }
        .warning-state {
            background-color: #fff3cd;
            border-left: 6px solid #ffeeba;
        }
        table, th, td {
          border: 1px solid black;
          border-collapse: collapse;
          padding: 8px;
          text-align: center;
        }

      </style>
    </head>
    """
    

    html_template += f"""
    <body>

        <h1>MDT Analysis Report</h1>

        <!-- Error State Section -->
        <div class="section error-state">
            <h2>Error State</h2>
            <div class="content">
                <p>{pmu_train_status}</p>
                
                <table border='1'>
                {summary_table}
                </table>
            </div>
        </div>

        <!-- Analysis State Section -->
        <div class="section warning-state">
            <h2>Analysis Result</h2>
            <div class="content">
                <p>{analysis_result}</p>

            </div>
        </div>

        <!-- Warning State Section -->
        <div class="section warning-state">
            <h2>Warning State</h2>
            <div class="content">
                <p>{wl_rxen_seq}</p>


            </div>
        </div>
        
        <!-- Missing Printing Section -->
        <div class="section warning-state">
            <h2>Missing Printing in file:</h2>
            <div class="content">
                <p>{missing_print_summary}</p>


            </div>
        </div>

    </body>
    <script>       
    </script>
    </html>
    """
    

    f = open(mdt_html, 'w')   
    f.write(html_template)    
    f.close()