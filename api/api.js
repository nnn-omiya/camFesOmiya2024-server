var app = require('express')();
var http = require('http').Server(app);
var socketio = require('socket.io');
var mysql      = require('sync-mysql');
var exec = require('child_process').exec

const port = 8080;

var connection = new mysql({
    host     : 'localhost',
    database : 'store',
    user     : 'root',
    password : ''
  });

const io = socketio(http);

// Middleware to set CORS header
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  next();
});

// Endpoint to get prices
app.get('/getprice', (req, res) => {
  try {
    const results = connection.query('SELECT * FROM item');
    const array = results.map(row => ({
      name: row.name,
      price: row.price,
      stock: row.stock
    }));
    res.json(array);
  } catch (err) {
    console.error("Database query failed: ", err.message);
    res.status(500).send('Database query failed');
  }
});

// Endpoint to get orders
app.get('/getorder', (req, res) => {
  try {
    const results = connection.query(`
      SELECT order_list.flag, oi.* 
      FROM order_list 
      INNER JOIN order_item AS oi ON order_list.orderID = oi.orderID
    `);
    const array = results.map(row => ({
      orderID: row.orderID,
      item: row.item,
      quantity: row.quantity,
      flag: row.flag
    }));
    res.json(array);
  } catch (err) {
    console.error("Database query failed: ", err.message);
    res.status(500).send('Database query failed');
  }
});

http.listen(port, () => {
    log(0,`listening on port ${port}`);
  });

io.sockets.on('connection', function (socket) {
    socket.emit('connected', 'connected');

    socket.on('order', (message) => {
      //オーダーIDを生成して ok?ls /
      //SQL order_listに追加して
      //SQL order_item に商品と個数を追加する
      /*log(0,message);*/
      let items = JSON.parse(message);
      let orderID = "";

      let max = connection.query('SELECT MAX(INTERNAL_ID) FROM order_list')[0]["MAX(INTERNAL_ID)"];

      //0埋めしたオーダーIDを生成
      if (items[0]["type"] == "mobile") { orderID="M"; }
      orderID += (max+1).toString().padStart( 3, '0');

      print_arg = orderID;
      log_text = "";

      time = Math.round((new Date()).getTime() / 1000);
      connection.query('INSERT INTO order_list (INTERNAL_ID, timestamp, orderID, flag) VALUES (NULL, ?, ?, 0)', [time, orderID])

      items.forEach((item,index) => {
        if(index === 0){ return; }
        connection.query('INSERT INTO order_item (INTERNAL_ID, orderID, item, quantity) VALUES (NULL, ?, ?, ?)', [orderID, item["item"], item["quantity"]])
        print_arg += " "+item["quantity"];
        log_text += item["quantity"]+",";
      });

      let array = {
        "status":"success",
        "orderID":orderID
      }

        exec('/usr/bin/python3 ../camfes/print.py '+print_arg, function(err, stdout, stderr) {
          if (stdout) console.log('stdout', stdout)
          if (stderr) console.log('stderr', stderr)
          if (err !== null) console.log('err', err)
        })
      socket.emit('order_end', array);
      log(1,log_text);

      order_data = items.slice(1);
      new_data = []
      new_data.push({"orderID": orderID, "items": order_data, "flag": 0})
      io.emit('order_share', new_data);
    });
    
    socket.on('available', (message) => {
      log(0,'available Message has been sent: '+message);
      io.emit('updateMonitor', message);
      connection.query('UPDATE order_list SET flag = 1 WHERE orderID = ?', [message]);
    });

    socket.on('complete', (message) => {
      log(0,'complete Message has been sent: '+message);
      io.emit('updateMonitor2', message);
      connection.query('UPDATE order_list SET flag = 2 WHERE orderID = ?', [message]);
    });
    // クライアントが切断したときの処理
    socket.on('disconnect', function() {});
});

function log(type,text) {
  console.log(Math.round((new Date()).getTime()/1000)+","+type+","+text)
}