
const express = require('express');
const server = express();

server.all('/', (req, res) => {
  res.send('<h2>Server is ready!</h2>');
});

module.exports = () => {
  server.listen(4000, () => {
    console.log('Server Ready.');
  });
  return true;
}
