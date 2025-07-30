const fs_node = require("fs");

let idxstr
try{
    idxstr = fs_node.readFileSync("src/simplex.html", "utf8")
}
catch{
	console.log("Error: cannot load simplex.html")
	process.exit();
}

let lines = idxstr.split("\n");
let ellines = [];
for(let n = 0; n < lines.length; n++){
	if(lines[n].indexOf("gen_code_help.js") >= 0){
		continue;
	}
	if(lines[n].indexOf("numeric-1.2.6.min.js") >= 0){
		continue;
	}
	ellines.push(lines[n]);
}
let outstr = ellines.join("\n");
outstr = outstr.replaceAll("src=\"", "src=\"/").replaceAll("href=\"", "href=\"/");
fs_node.writeFileSync("src/index.html", outstr, "utf8");

process.exit();
