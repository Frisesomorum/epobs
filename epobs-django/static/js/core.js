function formatCurrency(n) {
  var negative = (n < 0);
  n = Math.abs(Number(n) || 0);
  var i = String(parseInt(n.toFixed(2))),
    j = (j = i.length) > 3 ? j % 3 : 0;

  var abs = "$" + (j ? i.substr(0, j) + "," : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + ",") + "." + Math.abs(n - i).toFixed(2).slice(2);
  return negative ? "(" + abs + ")" : abs;
};
