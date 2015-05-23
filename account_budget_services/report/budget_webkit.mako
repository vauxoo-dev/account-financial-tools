<!DOCTYPE html SYSTEM
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body style="border:0;"> 
    %for obj in objects :
    <table class="table">
        <tr>
          <td class="active">1</td>
          <td class="success">2</td>
          <td class="warning">3</td>
          <td class="danger">4</td>
          <td class="info">5</td>
        </tr>
        <tr>
          <td class="active">1</td>
          <td class="success">2</td>
          <td class="warning">3</td>
          <td class="danger">4</td>
          <td class="info">5</td>
        </tr>
    </table>
    %endfor
</body>
</html>
