error_page = """
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <title>Error {{code}}</title>
    <style>
    html{background-color:#eee;}
    html,body{height:100%}
    h1{font-weight:100;}
    body{margin:0em; display:flex; align-items:center; justify-content:center;}
    h1,p{max-width:20em; margin:0.5em auto; text-align:center;}
    .logo{border-radius:4px;width:120px; background-color:orange; margin-bottom:10px;}
    </style>
  </head>
  <body>
    <div>
      <div class="logo" style="height: 35px;"></div>
      <div class="logo" style="height: 20px;"></div>
      <div class="logo" style="height: 10px;"></div>
      <h1>Error {{code}}</h1>
      <span>{{message}}</span>
    </div>
  </body>
</html>
"""

reload_page = """
           \|/
          (0 0)
+---oOO----(_)----------+
|                       |
|   R E L O A D E D !   |
|                       |
+----------------oOO----+
         |__|__|
          || ||
         ooO Ooo
"""
