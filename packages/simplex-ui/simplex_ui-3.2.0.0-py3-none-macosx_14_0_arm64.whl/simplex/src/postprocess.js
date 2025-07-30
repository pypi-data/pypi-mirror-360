"use strict";

var PPFormats = {};
var AnimationInterval = 100;

PPFormats.idxpair4d = [
    [[0, 1], [2, 3]], /* x, y */
    [[2, 3], [0, 1]], /* x', y' */
    [[0, 2], [1, 3]], /* x, x' */
    [[1, 3], [0, 2]]  /* y, y' */
];
PPFormats.idxpair3d = [
    [[0, 1], [2]], 
    [[0], [1, 2]],
    [[1], [0, 2]],
    [[2], [0, 1]],
    [[0, 2], [1]], 
    [[1, 2], [0]], 
];
PPFormats.idxpair2d = [
    [[0], [1]], /* x */
    [[1], [0]], /* y */
    [[0, 1], []], /* x, y */
];

// import the output data for post-processor (via. emscripten)
function SetOutput(dataname, data)
{
    if(dataname != ""){
        GUIConf.postprocessor.LoadOutputFile(data, dataname, true);
    }
    else{
        console.log(data);
    }
}

// change the plotly.js options
function ChangePlotOptions(changes)
{
    if(GUIConf.plotly == null){
        return;
    }
    GUIConf.plotly.ChangeOptionDirect(changes);
}

// select plotting type: line -> scatter, with markers -> scattergl
function ArrangeWebGL(data)
{
    for(let j = 0; j < data.length; j++){
        if(data[j].hasOwnProperty("mode") && data[j].hasOwnProperty("type")){
            if(data[j].type != "scatter3d"){
                if(data[j].mode == "markers" || data[j].mode == "lines+markers"){
                    data[j].type = "scattergl";
                }
                else{
                    data[j].type = "scatter";
                }
            }
        }
    }
}

// class to handle the plotly.js object
class PlotWindow {
    constructor(parent, id, plobj, setting, plotname, subcols = null, 
            frameindices = [], tmval = -1, cloffset = 0, sliderparent = null, 
            hideslider = false, layoutini = null, link2d = false){
        this.m_parent = parent;
        this.m_isnew = true;
        this.m_ploptions = setting;
        Object.keys(PlotOptionsLabel).forEach(key => {
            let label = PlotOptionsLabel[key][0];
            if(!this.m_ploptions.hasOwnProperty(label)){
                this.m_ploptions[label] = PlotOptionsLabel[key][1];
            }
        })
        this.m_plotname = plotname == ""?"untitled":plotname;
        this.m_layout = {};
        this.m_layoutini = layoutini;
        this.m_cloffset = cloffset;
        this.m_slave = false;
        this.m_subcols = subcols;
        this.m_link2d = link2d;
        this.m_title = "";

        if(tmval >= 0){
            AnimationInterval = tmval;
        }

        let plotdiv = document.createElement("div");
        this.m_parent.appendChild(plotdiv);
        plotdiv.id = id;       
        plotdiv.className = "flex-grow-1";

        plotdiv.addEventListener("editplotly", (e)=>{    
            this.EditPlot();
        });      

        this.m_data = plobj.data;
        this.m_dimension = plobj.dimension;
        this.m_id = id;
        this.m_isanim = frameindices.length > 0;
        this.m_axtitles = plobj.axtitles;
        this.m_scatter = plobj.scatter;
        if(this.m_scatter){
            this.m_ploptions[PlotOptionsLabel.type[0]] = SymbolLabel;
        }

        if(this.m_isanim){
            this.m_fdata = plobj.fdata;
        }
        let config = this.GetConfig();
        if(this.m_isanim){
            this.m_animlegend = plobj.animlegend;
            this.m_compdata = plobj.compdata;
            this.m_vardata = plobj.vardata;
            this.m_ftitles = plobj.ftitles;

            // slider setting
            this.m_sliderdiv = document.createElement("div");
            if(sliderparent != null){
                sliderparent.appendChild(this.m_sliderdiv);
            }
            else{
                this.m_parent.appendChild(this.m_sliderdiv);
            }
            this.m_sliderdiv.className = "d-flex justify-content-center w-100";
            if(hideslider){
                this.m_sliderdiv.className = "d-none";
                this.m_slave = true;
            }

            this.m_animdiv = document.createElement("div");
            this.m_animdiv.className = "d-flex align-items-center";
            let intrvtitle = document.createElement("div");
            intrvtitle.innerHTML = "Interval (ms)";
            intrvtitle.style.margin = "0px 5px";
            this.m_animintrv = document.createElement("input");
            this.m_animintrv.setAttribute("type", "number");
            this.m_animintrv.min = 0;
            this.m_animintrv.max = 2000;
            this.m_animintrv.step = 50;
            this.m_animintrv.style.width = "50px";
            this.m_animintrv.value = AnimationInterval;
            this.m_animintrv.addEventListener("change", (e) => 
                {
                    AnimationInterval = e.currentTarget.value;
                }
            )
    
            this.m_animbtn = document.createElement("button");
            this.m_animbtn.innerHTML = "&#9654;"
            this.m_animbtn.className = "btn btn-primary btn-sm";
            this.m_animbtn.addEventListener("click", (e)=>{
                if(this.onanimation){
                    this.StopAnimation();
                }
                else{
                    let slides = this.GetSlideNumber();
                    if(slides[0] == slides[1]){
                        // return to 0-th slide
                        this.SetSlideNumber(0);
                    }
                    this.StartAnimation();
                }
                this.SwitchAnimationButton(this.onanimation);
            });
            this.m_animdiv.appendChild(intrvtitle);
            this.m_animdiv.appendChild(this.m_animintrv);
            this.m_animitem = 0;
            if(this.m_ftitles[1] != ""){
                let animselect = document.createElement("select");
                SetSelectMenus(animselect, this.m_ftitles, [], this.m_ftitles[0]);
                this.m_animdiv.appendChild(animselect);
                animselect.addEventListener("change", (e) => {
                    this.m_animitem = Math.max(0, e.currentTarget.selectedIndex);
                });
            }
            this.m_animdiv.appendChild(this.m_animbtn);
            this.m_sliderdiv.appendChild(this.m_animdiv);

            this.m_slider = [];
            this.m_sliderlabel = [];
            for(let i = 0; i < 2; i++){
                let divcont = document.createElement("div");
                divcont.className = "d-flex align-items-center";

                this.m_slider.push(document.createElement("input"));
                this.m_slider[i].className = "m-1 slider";
                this.m_slider[i].type = "range";
                this.m_slider[i].max = this.m_fdata[i].length-1;
                let framelen = 0;
                let nfmax = 0;
                for(let nf = 0; nf < this.m_fdata[i].length; nf++){
                    let ftitle = this.m_ftitles[i];
                    ftitle = ftitle.replaceAll("<sub>", "");
                    ftitle = ftitle.replaceAll("</sub>", "");
                    ftitle = ftitle.replaceAll("&", "");
                    ftitle = ftitle.replaceAll(";", "");
                    let len = (ftitle+"="+ToPrmString(this.m_fdata[i][nf], 3)).length;
                    if(len > framelen){
                        framelen = len;
                        nfmax = nf;
                    }
                }
                this.m_slider[i].value = frameindices[i];
                this.m_slider[i].addEventListener("change",
                    (e) => {
                        if(this.m_link2d){
                            this.m_slider[1-i].value = e.currentTarget.value;
                        }
                        this.ShowSlide();
                    });
                divcont.appendChild(this.m_slider[i]);

                this.m_sliderlabel.push(document.createElement("div"));
                this.m_sliderlabel[i].innerHTML = "";
                this.m_sliderlabel[i].style.minWidth = framelen.toString()+"ex";
                divcont.appendChild(this.m_sliderlabel[i]);

                if(this.m_ftitles[i] == ""){
                    divcont.classList.add("d-none");
                }
                this.m_sliderdiv.appendChild(divcont);
            }
            if(this.m_ftitles[1] == ""){
                this.m_slider[1].value = 0;
            }
            this.SetRangesAnim();            
            if(this.m_dimension == 1){
                let range = this.GetRanges(config);
                this.m_layout = GetLayout1D(this.m_axtitles, range.linear, range.log, config.xyscale);
                if(this.m_layoutini != null){
                    this.m_layout = this.m_layoutini;
                }
            }
            else{
                this.m_ztitle = plobj.ztitle;
                this.m_layout = {
                    "surface": GetLayout2D(this.m_vardata.length, false, this.m_axtitles, 
                        this.m_axtitles.slice(2), null, this.m_ranges[2], this.m_subcols),
                    "heatmap": GetLayout2D(this.m_vardata.length, true, this.m_axtitles, 
                        this.m_axtitles.slice(2), this.m_ranges, this.m_ranges[2], this.m_subcols),
                    "ztitle" : this.m_ztitle
                };
                if(this.m_layoutini != null){
                    if(this.m_ploptions[PlotOptionsLabel.type2d[0]] == ContourLabel){
                        this.m_layout.heatmap = this.m_layoutini;
                    }
                    else{
                        this.m_layout.surface = this.m_layoutini;
                    }
                }
            }
            this.ShowSlide(true);
            this.SetupRelayout(this.m_id);
        }
        else{
            this.m_titles = plobj.titles;
            this.m_legprefix = plobj.legprefix;
            this.m_isdata2d = plobj.isdata2d;
            this.PlotObject(this.m_id, this.m_data, this.m_dimension, 
                this.m_titles, this.m_axtitles, this.m_legprefix, this.m_isdata2d, config.xyscale);
            this.SetupRelayout(this.m_id);
        }
    }

    IsAnimation()
    {
        if(!this.m_isanim){
            return false;
        }
        return this.m_fdata[0].length > 1 || this.m_fdata[1].length > 1;
    }

    GetClientSize(){
        return [this.m_parent.clientWidth, this.m_parent.clientHeight];
    }

    GetParent(){
        return this.m_parent;
    }

    GetData(){
        let plobj = {};
        plobj.data = this.m_data;
        plobj.dimension = this.m_dimension;
        plobj.axtitles = this.m_axtitles;
        plobj.plotname  = this.m_plotname;
        plobj.scatter = this.m_scatter;
        plobj.link2d = this.m_link2d;

        plobj.size = this.GetClientSize()

        plobj.frameindices = [];
        plobj.tinv = 100;
        plobj.setting = CopyJSON(this.m_ploptions);
        if(this.m_isanim){
            plobj.animlegend = this.m_animlegend;
            plobj.compdata = this.m_compdata;
            plobj.vardata = this.m_vardata;
            plobj.ftitles = this.m_ftitles;
            plobj.fdata = this.m_fdata;
            plobj.frameindices = [this.m_slider[0].value, this.m_slider[1].value];
            plobj.tinv  = this.m_animintrv.value;
            if(this.m_dimension == 2){
                plobj.ztitle = this.m_ztitle;
            }
        }
        else{
            plobj.titles = this.m_titles;
            plobj.legprefix = this.m_legprefix;
            plobj.isdata2d = this.m_isdata2d;
        }
        plobj.layout = null;

        let plotly = document.getElementById(this.m_id);
        if(plotly.hasOwnProperty("layout")){
            plobj.layout = CopyJSON(plotly.layout);
        }
        return CopyJSON(plobj);
    }

    GetRanges(config){
        let ranges = null;
        let logranges = this.m_logranges;
        if(this.m_isanim){
            if(config.normeach){
                let index = [];
                for(let j = 0; j < 2; j++){
                    index.push(parseInt(this.m_slider[j].value));
                }
                logranges = this.m_lograneach[index[1]][index[0]];
            }
            else{
                ranges = this.m_ranges;
            }
        }
        return {linear:ranges, log:logranges};
    }

    PutTitle(title){
        this.m_title = title;
        this.RefreshPlotObject();
    }

    SetTitle(layout){
        if(this.m_title != ""){
            layout.title = {text: this.m_title, automargin: true};
            layout.title.font = CopyJSON(PlotlyFont);
            layout.title.font.size += 2;
            layout.title.font.style = "italic";
        }
    }

    PlotObject(id, obj, dim, titles, axtitles, legprefix, isdata2d, xyscale)
    // isdata2d: input data is 2-dimensional (true: data[x][y]) or 1-dim. (false: data[x+Ny])
    {
        let plotobj = this.CreatePlotObj(id, obj, dim, titles, axtitles, legprefix, isdata2d, xyscale);
        let config = this.GetConfig();
        let layout;
        if(dim == 0 || dim == 1){
            this.m_layout = GetLayout1D(axtitles, null, this.m_logranges, xyscale);
            if(this.m_layoutini != null){
                this.m_layout = this.m_layoutini;
            }
            if(plotobj.length == 1){
                this.m_layout.showlegend = false;
            }
            layout = this.m_layout;
        }
        else{
            layout = this.m_layout[config.type2d];
        }
        ArrangeWebGL(plotobj);
        this.SetTitle(layout);
        Plotly.newPlot(id, plotobj, layout, PlotlyPrms.config);
    }

    CreatePlotObj(id, obj, dim, titles, axtitles, legprefix, isdata2d, xyscale)
    {
        let plotobj;
        let config = this.GetConfig();
        if(dim == 0 || dim == 1){
            if(dim == 1){
                plotobj = [];
                for(let i = 0; i < obj.length; i++){
                    let legends = [];
                    if(i < legprefix.length){
                        if(titles.length > 2){
                            for(let j = 1; j < titles.length; j++){
                                legends.push(titles[j]+":"+legprefix[i]);
                            }
                        }
                        else{
                            legends.push(legprefix[i]);
                        }    
                    }
                    let plotobjr = GetPlotConfig1D(obj[i], titles[0], titles.slice(1), legends, config.mode);
                    for(let j = 0; j < plotobjr.length; j++){
                        plotobj.push(plotobjr[j]);
                    }
                }
            }
            else{
                plotobj = GetPlotConfig0D(obj[0], titles, config.mode);
                axtitles.push(titles[0]);
            }
            this.SetRanges(plotobj);
            this.m_layout = GetLayout1D(axtitles, null, this.m_logranges, xyscale);
            if(this.m_layoutini != null){
                this.m_layout = this.m_layoutini;
            }
            if(plotobj.length == 1){
                this.m_layout.showlegend = false;
            }
            for(let j = 0; j < plotobj.length; j++){
                plotobj[j].line = this.GetLine(j, config.width);
                plotobj[j].marker = this.GetMarker(j, config.size);
            }
            this.m_nplots = plotobj.length;
        }
        else{
            let pobj = GetPlotConfig2D(obj, titles, axtitles, config, isdata2d); 
            this.m_nplots = pobj.nplots;
            plotobj = pobj.data;
            this.m_layout = pobj.layout;
            if(this.m_layoutini != null){
                if(this.m_ploptions[PlotOptionsLabel.type2d[0]] == ContourLabel){
                    this.m_layout.heatmap = this.m_layoutini;
                }
                else{
                    this.m_layout.surface = this.m_layoutini;
                }
            }
            this.SetRanges(plotobj);
        }
        return plotobj;
    }

    GetLine(j, defw)
    {
        j += this.m_cloffset;
        let nc = PlotlyColors.length;
        let m = j % nc;
        let n = Math.floor(j/nc) % nc;
        let k = Math.floor(j/nc/nc)+defw;
        let color = [0, 0, 0];
        let clstr = "rgb("
        for(let i = 0; i < 3; i++){
            if(n > 0){
                if(m == n){
                    color[i] = PlotlyColors[m][i]/2;
                }
                else{
                    color[i] = (PlotlyColors[m][i]+PlotlyColors[n][i])/2;
                }
            }
            else{
                color[i] = PlotlyColors[m][i];
            }
            if(i > 0){
                clstr += ",";
            }
            clstr += color[i].toString();
        }
        clstr += ")";
        return {width: k, color: clstr};
    }

    GetMarker(j, defs)
    {
        let i = j % PlotlyMarkers.length;
        return {symbol: PlotlyMarkers[i], size:defs};
    }

    ChangeLegend(index, text)
    {
        let data = document.getElementById(this.m_id).data;
        data[index].name = text;
    }

    RefreshPlotObject(changes = [], opr = {})
    {
        let config = this.GetConfig();
        let data = document.getElementById(this.m_id).data;
        if(opr.hasOwnProperty("type")){
            if(opr.type == "delete"){
                if(opr.index < this.m_nplots){
                    data.splice(opr.index, 1);
                    this.m_nplots--;
                }
            }
            else if(opr.type == "set"){// add or replace data based on legend
                let n;
                for(n = 0; n < this.m_nplots; n++){
                    if(data[n].name == opr.text){
                        break;
                    }
                }
                if(n == this.m_nplots){
                    let newdata = {};
                    newdata.line = this.GetLine(n, config.width);
                    newdata.marker = this.GetMarker(n, config.size);
                    newdata.mode = data[0].mode;
                    if(opr.hasOwnProperty("mode")){
                        newdata.mode = opr.mode;
                    }
                    newdata.name = opr.text;
                    newdata.type = data[0].type;
                    newdata.x = opr.newdata[0];
                    newdata.y = opr.newdata[1];    
                    data.push(newdata);
                    this.m_nplots++;
                }
                else{
                    data[n].x = opr.newdata[0];
                    data[n].y = opr.newdata[1];
                    data[n].name = opr.text;
                }
            }
            else if(opr.type == "replace"){// add or replace data based on index
                let newdata = {};
                newdata.line = this.GetLine(opr.index, config.width);
                newdata.marker = this.GetMarker(opr.index, config.size);
                newdata.mode = data[0].mode;
                if(opr.hasOwnProperty("mode")){
                    newdata.mode = opr.mode;
                }
                newdata.type = data[0].type;
                newdata.x = opr.newdata[0];
                if(opr.newdata.length > 1){
                    newdata.y = opr.newdata[1];
                }
                else if(opr.index < this.m_nplots){
                    newdata.y = data[opr.index].y;
                }
                else{
                    return;
                }
                if(opr.hasOwnProperty("text")){
                    newdata.name = opr.text;
                }
                else{
                    newdata.name = data[opr.index].name;
                }

                if(opr.index < this.m_nplots){
                    data[opr.index] = newdata;
                }
                else{
                    data.push(newdata);
                }    
            }
            else if(opr.type == "revise"){// revise the base data
                this.m_legprefix = opr.obj.legprefix;
                let plotobj = this.CreatePlotObj(this.m_id, opr.obj.data, this.m_dimension, 
                        this.m_titles, this.m_axtitles, this.m_legprefix, this.m_isdata2d, config.xyscale);
                for(let n = 0; n < plotobj.length; n++){
                    data[n] = plotobj[n];
                }
            }
            this.m_layout.showlegend = this.m_nplots > 1;
        }
        if(opr.hasOwnProperty("xaxis")){
            this.m_axtitles[0] = opr.xaxis;
            changes.push(PlotOptionsLabel.xscale[0]);
        }
        if(opr.hasOwnProperty("yaxis")){
            this.m_axtitles[1] = opr.yaxis;
            changes.push(PlotOptionsLabel.yscale[0]);
        }

        let layoutnew, layout;
        if(changes.length > 0){
            if(this.m_dimension == 1){
                let range = this.GetRanges(config);
                layoutnew = GetLayout1D(this.m_axtitles, range.linear, range.log, config.xyscale);
                for(let n = 0; n < this.m_nplots; n++){
                    data[n].mode = config.mode;
                    data[n].line.width = config.width;
                    data[n].marker.size = config.size;
                }
            }
            else{
                let ndpl = data.length/this.m_nplots;
                let orgdata = [];
                for(let n = 0; n < this.m_nplots; n++){
                    orgdata.push(data[n*ndpl]);
                }
                data.length = 0;
                for(let n = 0; n < this.m_nplots; n++){                    
                    Set2DPlotObjects(orgdata[n].x, orgdata[n].y, orgdata[n].z, this.m_ranges[2], config, n, this.m_nplots, data, "", orgdata[n]);
                }
                layoutnew = GetLayout2D(this.m_nplots, config.type2d == "heatmap", 
                    this.m_axtitles, this.m_axtitles.slice(2), null, this.m_ranges[2], this.m_subcols);
            }            
        }
        let xyr = ["xrange", "yrange"];
        let xys = ["xaxis", "yaxis"];
        let xyc = ["xscale", "yscale"];
        let xya = ["xauto", "yauto"];
        for(let j = 0; j < changes.length; j++){
            for(let i = 0; i < 2 && layoutnew.hasOwnProperty(xys[i]); i++){
                if(changes[j] == PlotOptionsLabel[xyr[i]][0]){
                    if(config.xyscale[i] == "log"){
                        layoutnew[xys[i]].range = 
                        [
                            Math.log10(this.m_ploptions[PlotOptionsLabel[xyr[i]][0]][0]),
                            Math.log10(this.m_ploptions[PlotOptionsLabel[xyr[i]][0]][1])
                        ];
                    }
                    else{
                        layoutnew[xys[i]].range = this.m_ploptions[PlotOptionsLabel[xyr[i]][0]];
                    }
                }
                if(changes[j] == PlotOptionsLabel[xya[i]][0]){
                    layoutnew[xys[i]].autorange = this.m_ploptions[PlotOptionsLabel[xya[i]][0]];
                    if(this.m_dimension == 1 && this.IsAnimation() && i == 1){
                        layoutnew[xys[i]].autorange = layoutnew[xys[i]].autorange && config.normeach;
                    }
                }
                for(let n = 2; n <= this.m_nplots && this.m_dimension == 2; n++){
                    let xyl = xys[i]+n.toString();
                    let autor = false;
                    if(layoutnew[xys[i]].hasOwnProperty("autorange")){
                        autor = layoutnew[xys[i]].autorange;
                        layoutnew[xyl].autorange = autor;
                    }
                    if(autor){
                        delete layoutnew[xyl].range;
                    }
                    else{
                        if(layoutnew[xys[i]].hasOwnProperty("range")){
                            layoutnew[xyl].range = Array.from(layoutnew[xys[i]].range);
                        }
                    }
                }
                if(changes[j] == PlotOptionsLabel[xyc[i]][0] 
                        || changes[j] == PlotOptionsLabel[xyr[i]][0]
                        || changes[j] == PlotOptionsLabel[xya[i]][0])
                {
                    if(this.m_dimension == 1){
                        this.m_layout[xys[i]] = CopyJSON(layoutnew[xys[i]]);
                    }
                    else if(config.type2d == "heatmap"){
                        Object.assign(this.m_layout[config.type2d][xys[i]], layoutnew[xys[i]]);
                        for(let n = 2; n <= this.m_nplots; n++){
                            let xyl = xys[i]+n.toString();
                            Object.assign(this.m_layout[config.type2d][xyl], layoutnew[xyl]);
                        }
                    }
                }    
            }
            if(changes[j] == PlotOptionsLabel.normalize[0]){
                if(this.m_dimension == 1){
                    this.m_layout.yaxis = CopyJSON(layoutnew.yaxis);
                }
                else{
                    if(config.type2d == "surface"){
                        for(let n = 0; n < this.m_nplots; n++){
                            let scn = GetSceneName(n);
                            this.m_layout["surface"][scn].zaxis = CopyJSON(layoutnew[scn].zaxis);
                        }
                    }
                    this.m_layout["surface"].zaxis = CopyJSON(layoutnew.zaxis);
                    this.m_layout["heatmap"].zaxis = CopyJSON(layoutnew.zaxis);
                }
            }
        }
        if(this.m_dimension == 1){
            layout = this.m_layout;
        }
        else{
            layout = this.m_layout[config.type2d];
        }
        Plotly.purge(this.m_id);
        ArrangeWebGL(data);
        this.SetTitle(layout);
        Plotly.newPlot(this.m_id, data, layout, PlotlyPrms.config);
        this.SetupRelayout(this.m_id);
        if(this.m_isanim && this.m_dimension == 2){
            this.ShowSlide();
        }
    }
    
    Plot1DAmination(id, layout, nplots, vararr, sliceobj, legend, compdata, frameno)
    {
        let config = this.GetConfig();
        let data = [];

        for(let j = 0; j < nplots; j++){
            if(this.m_scatter){
                data.push(
                    {
                        x: sliceobj[j][frameno[1]][frameno[0]][0],
                        y: sliceobj[j][frameno[1]][frameno[0]][1],
                        type: PlotlyScatterType,
                        name: legend[j],
                        mode: config.mode,
                        line: this.GetLine(j, config.width),
                        marker: this.GetMarker(j, config.size)
                    }
                );            
            }
            else{
                data.push(
                    {
                        x: vararr[j],
                        y: sliceobj[j][frameno[1]][frameno[0]][0],
                        type: PlotlyScatterType,
                        name: legend[j],
                        mode: config.mode,
                        line: this.GetLine(j, config.width),
                        marker: this.GetMarker(j, config.size)
                    }
                );            
            }
        }
        if(nplots == 1){
            layout.showlegend = false;
        }
        for(let i = 0; i < compdata.length; i++){
            compdata[i].mode = config.mode;
            compdata[i].line = this.GetLine(i+nplots, config.width);
            compdata[i].marker = this.GetMarker(i+nplots, config.size);
            data.push(compdata[i]);
        }
        this.m_nplots = data.length;

        ArrangeWebGL(data);
        this.SetTitle(layout);
        if(this.m_isnew){
            Plotly.newPlot(id, data, layout, PlotlyPrms.config);
            this.m_isnew = false;
        }
        else{
            if(document.getElementById(id).hasOwnProperty("data")){
                let dataorg = document.getElementById(id).data;
                if(dataorg.length == this.m_nplots){
                    for(let j = 0; j < this.m_nplots; j++){
                        if(dataorg[j].hasOwnProperty("visible")){
                            data[j].visible = dataorg[j].visible;
                        }
                    }
                }    
            }
            Plotly.react(id, data, layout);
        }
    }        

    Plot2DAnimation(id, layout, vararr, sliceobj, frameno, config, titles)
    {
        let normeach = config.normeach;
        let data = [];
        this.m_nplots = vararr.length;
        for(let n = 0; n < this.m_nplots; n++){
            Set2DPlotObjects(vararr[n][0], vararr[n][1], 
                sliceobj[n][frameno[1]][frameno[0]], this.m_ranges[2], config, n, this.m_nplots, data, titles[n]);
        }

        let layoutloc = layout[config.type2d];
        if(normeach){
            let ndpl = data.length/this.m_nplots;
            for(let n = 0; n < data.length; n += ndpl){
                delete data[n].zmax;
                delete data[n].zmin;
            }
            if(config.type2d == "surface"){
                for(let n = 0; n < this.m_nplots; n++){
                    if(layoutloc[GetSceneName(n)].hasOwnProperty("zaxis")){
                        delete layoutloc[GetSceneName(n)].zaxis.range;
                    }
                }
            }
        }
        if(this.m_nplots > 1){
            AddAnnotations(layoutloc, config.type2d == "surface", this.m_nplots, titles);
        }

        ArrangeWebGL(data);
        this.SetTitle(layoutloc);
        if(this.m_isnew){
            Plotly.newPlot(id, data, layoutloc, PlotlyPrms.config);
            this.m_isnew = false;
        }
        else{
            Plotly.react(id, data, layoutloc);    
        }
    }
  
    SetRangesAnim(){
        this.m_ranges = [[], [], []];
        this.m_logranges = [[], [], []];

        let frames = [this.m_data[0].length, this.m_data[0][0].length];
        let scranges = new Array(this.m_dimension+1);
        let rangesk = new Array(this.m_dimension+1);

        this.m_lograneach = new Array(frames[0]);
        let ranges;
        for(let i = 0; i < frames[0]; i++){
            this.m_lograneach[i] = new Array(frames[1]);
            for(let j = 0; j < frames[1]; j++){
                let rangeeach;
                if(this.m_link2d && i != j){
                    continue;
                }
                for(let n = 0; n < this.m_data.length; n++){
                    let mesh = [this.m_data[n][i][j].length, this.m_data[n][i][j][0].length];
                    for(let k = 0; k < mesh[0]; k++){
                        for(let l = 0; l < mesh[1]; l++){
                            let f = this.m_data[n][i][j][k][l];
                            if(n+i+j+k+l == 0){
                                ranges = [f, f];
                            }
                            else{
                                ranges[0] = Math.min(ranges[0], f);
                                ranges[1] = Math.max(ranges[1], f);
                            }
                            if(this.m_scatter){
                                if(n+i+j+l == 0){
                                    rangesk[k] = [f, f];
                                }
                                else{
                                    rangesk[k][0] = Math.min(rangesk[k][0], f);
                                    rangesk[k][1] = Math.max(rangesk[k][1], f);
                                }    
                            }
                            if(n+k+l == 0){
                                rangeeach = [f, f];
                            }    
                            else{
                                rangeeach[0] = Math.min(rangeeach[0], f);
                                rangeeach[1] = Math.max(rangeeach[1], f);
                            }
                        }
                        if(this.m_scatter){
                            if(k == mesh[0]-1){
                                if(n == 0){
                                    this.m_lograneach[i][j] = rangeeach;    
                                }
                                else{
                                    this.m_lograneach[i][j][0] = Math.min(this.m_lograneach[i][j][0], rangeeach[0]);
                                    this.m_lograneach[i][j][1] = Math.max(this.m_lograneach[i][j][1], rangeeach[1]);
                                }
                            }
                            if(n == 0){
                                scranges[k] = rangesk[k];
                            }
                            else{
                                scranges[k][0] = Math.min(scranges[k][0], rangesk[k][0]);
                                scranges[k][1] = Math.max(scranges[k][1], rangesk[k][1]);
                            }
                        }
                    }
                }
                if(!this.m_scatter){
                    this.m_lograneach[i][j] = rangeeach;    
                }
            }
        }

        if(this.m_scatter){
            for(let j = 0; j <= this.m_dimension; j++){
                this.m_ranges[j] = scranges[j];
            }    
        }
        else{
            for(let j = 0; j < this.m_dimension; j++){
                this.m_ranges[j] = [GetMin(this.m_vardata[0][j]), GetMax(this.m_vardata[0][j])];
            }
            for(let n = 1; n < this.m_vardata.length; n++){
                for(let j = 0; j < this.m_dimension; j++){
                    this.m_ranges[j] = [Math.min(this.m_ranges[j][0], GetMin(this.m_vardata[n][j])), 
                        Math.max(this.m_ranges[j][1], GetMax(this.m_vardata[n][j]))];
                }               
            }
             this.m_ranges[this.m_dimension] = ranges;   
        }

        for(let j = 0; j <= this.m_dimension; j++){
            this.m_logranges[j] = GetLogRange(this.m_ranges[j][0], this.m_ranges[j][1], LOGOFFSET);
        }
        let fullranges = ranges[1]-ranges[0];
        if(!this.m_scatter){
            this.m_ranges[this.m_dimension][0] -= fullranges*(LOGOFFSET-1)/2;
            this.m_ranges[this.m_dimension][1] += fullranges*(LOGOFFSET-1)/2;    
        }
    }

    SetRanges(plotobj){
        this.m_ranges = [];
        this.m_logranges = [];
        for(let j = 0; j <= this.m_dimension; j++){
            let range;
            for(let n = 0; n < plotobj.length; n++){
                let data;
                if(j == 0){
                    data = plotobj[n].x;
                }
                else if(j == 1){
                    data = plotobj[n].y;
                }
                else{
                    data = plotobj[n].z;
                }
                if(n == 0){
                    range = [GetMin(data), GetMax(data)];
                }
                else{
                    range[0] = Math.min(range[0], GetMin(data));
                    range[1] = Math.max(range[1], GetMax(data));
                }
            }
            this.m_ranges.push(range);
            this.m_logranges.push(GetLogRange(this.m_ranges[j][0], this.m_ranges[j][1], LOGOFFSET));
        }
    }
    
    EditPlot(){
        let isanm = this.IsAnimation();
        let ploption = new PlotOptions(this.m_dimension, isanm, this.m_nplots);
        this.m_ploptionsold =  CopyJSON(this.m_ploptions);
        let plobj = {};
        plobj = this.m_ploptionsold;
        ploption.JSONObj = plobj;

        let layout = document.getElementById(this.m_id).layout;
        if(layout.hasOwnProperty("xaxis")){
            let xys = ["xaxis", "yaxis"];
            let xyr = ["xrange", "yrange"];
            let xya = ["xauto", "yauto"];
            for(let i = 0; i < 2; i++){
                let xy = xys[i];
                if(layout[xy].type == "log"){
                    ploption.JSONObj[PlotOptionsLabel[xyr[i]][0]] = 
                        [10**(layout[xy].range[0]), 10**(layout[xy].range[1])];
                }
                else{
                    ploption.JSONObj[PlotOptionsLabel[xyr[i]][0]] = 
                        [layout[xy].range[0], layout[xy].range[1]];
                }
                let autor = false
                if(layout[xy].hasOwnProperty("autorange")){
                    autor = layout[xy].autorange;
                }
                ploption.JSONObj[PlotOptionsLabel[xya[i]][0]] = autor;
                this.m_ploptions[PlotOptionsLabel[xya[i]][0]] = autor;
                this.m_ploptions[PlotOptionsLabel[xyr[i]][0]] = 
                    Array.from(ploption.JSONObj[PlotOptionsLabel[xyr[i]][0]]);
            }
        }

        ploption.SetPanel();
        ShowDialog("Plot Configurations", true, false, "", ploption.GetTable(), 
            (() => {
                setTimeout(() => {
                    this.ChangeOption();
                    SwitchSpinner(false);
                }, 100);
                SwitchSpinner(true);
            }).bind(this)
        );
    }

    ChangeOptionDirect(changes){
        let keys = Object.keys(changes);
        this.m_ploptionsold = CopyJSON(this.m_ploptions);
        ["xrange", "yrange"].forEach((xy) => { // force to refresh for x/y range parameters
            if(changes.hasOwnProperty(xy)){
                this.m_ploptions[PlotOptionsLabel[xy][0]] = [null, null]
            }    
        });
        for(const key of keys){
            if(PlotOptionsOrder.includes(key)){
                if(Array.isArray(changes[key])){
                    this.m_ploptionsold[PlotOptionsLabel[key][0]] = Array.from(changes[key]);
                }
                else{
                    this.m_ploptionsold[PlotOptionsLabel[key][0]] = changes[key];
                }
            }
        }
        this.ChangeOption();
    }

    ChangeOption(){
        let changes = [];
        PlotOptionsOrder.forEach((e) => {
            if(Array.isArray(this.m_ploptionsold[PlotOptionsLabel[e][0]])){
                let isdif = false;
                for(let k = 0; k < this.m_ploptionsold[PlotOptionsLabel[e][0]].length; k++){
                    if(this.m_ploptionsold[PlotOptionsLabel[e][0]][k] != 
                            this.m_ploptions[PlotOptionsLabel[e][0]][k]){
                        isdif = true;
                        break;
                    }
                }
                if(isdif){
                    changes.push(PlotOptionsLabel[e][0]);
                }
            }
            else if(this.m_ploptionsold[PlotOptionsLabel[e][0]] != 
                this.m_ploptions[PlotOptionsLabel[e][0]])
            {
                changes.push(PlotOptionsLabel[e][0]);
            }            
        });
        if(changes.length == 0){
            return;
        }
        Object.keys(this.m_ploptionsold).forEach(el=>{
            this.m_ploptions[el] = this.m_ploptionsold[el];
        });
        this.RefreshPlotObject(changes);
    }
    
    GetSlideNumber(){
        return [parseInt(this.m_slider[this.m_animitem].value), parseInt(this.m_slider[this.m_animitem].max)];
    }

    SetSlideNumber(slide){
        this.m_slider[this.m_animitem].value = slide.toString();
        if(this.m_link2d){
            this.m_slider[1-this.m_animitem].value = slide.toString();
        }
    }   

    AdvanceSlide()
    {   
        let slides = this.GetSlideNumber();
        slides[0]++;
        if(slides[0] > slides[1]){
            this.StopAnimation();
            this.SwitchAnimationButton(false);
            return;
        }
        this.SetSlideNumber(slides[0]);
        this.ShowSlide();
    }
    
    StopAnimation()
    {
        clearInterval(this.animtimer);
        this.onanimation = false;
    }
   
    StartAnimation()
    {
        if(!this.m_isanim){
            return;
        }
        this.animtimer = setInterval(this.AdvanceSlide.bind(this), this.m_animintrv.value);
        this.onanimation = true;
    }

    SwitchSlide(slides)
    {
        for(let j = 0; j < 2; j++){
            if(this.m_ftitles[j] != ""){
                if(slides[j] < 0){
                    slides[j] = this.m_slider[j].max;
                }
                this.m_slider[j].value = slides[j].toString();
            }
        }
        this.ShowSlide();
    }

    GetSliceValue(){
        let slices = [];        
        for(let i = 0; i < 2; i++){
            slices.push(parseInt(this.m_slider[i].value));
            this.m_sliderlabel[i].innerHTML = this.m_ftitles[i]+"="
                +ToPrmString(this.m_fdata[i][slices[i]], 3);
        }
        return slices;
    }

    GetConfig(){
        let config = {};

        if(this.m_dimension == 2){
            config.xyscale = ["linear", "linear"];
        }
        else{
            config.xyscale = [
                this.m_ploptions[PlotOptionsLabel.xscale[0]] == LinearLabel ? "linear" : "log",
                this.m_ploptions[PlotOptionsLabel.yscale[0]] == LinearLabel ? "linear" : "log"
            ];    
        }

        switch(this.m_ploptions[PlotOptionsLabel.type[0]]){
            case LineLabel:
                config.mode = "lines";
                break;
            case LineSymbolLabel:
                config.mode = "lines+markers";
                break;
            case SymbolLabel:
                config.mode = "markers";
                break;                    
        }       

        config.wireframe = this.m_ploptions[PlotOptionsLabel.wireframe[0]]
        if(this.m_ploptions[PlotOptionsLabel.type2d[0]] == SurfaceLabel){
            config.typepl = config.type2d = "surface";
        }
        else if(this.m_ploptions[PlotOptionsLabel.type2d[0]] == SurfaceShadeLabel){
            config.typepl =  "mesh3d";
            config.type2d = "surface";
        }
        else{
            config.typepl = config.type2d = "heatmap";
            config.wireframe = false;
        }

        if(this.IsAnimation()){
            config.normeach = this.m_ploptions[PlotOptionsLabel.normalize[0]] == ForEachLabel;
            if(this.m_dimension == 1){
                config.normeach = config.normeach && this.m_ploptions[PlotOptionsLabel.yauto[0]];
            }
        }
        else{
            config.normeach = false;
        }
        if(this.m_ploptions[PlotOptionsLabel.colorscale[0]] == DefaultLabel){
            config.colorscale = PlotlyPrms.clscale;
        }
        else{
            config.colorscale = 
                this.m_ploptions[PlotOptionsLabel.colorscale[0]];
        }
        config.size = this.m_ploptions[PlotOptionsLabel.size[0]];
        config.width = this.m_ploptions[PlotOptionsLabel.width[0]];
        config.color = this.m_ploptions[PlotOptionsLabel.shadecolor[0]];
        config.showscale = this.m_ploptions[PlotOptionsLabel.showscale[0]];
        return config;        
    }
    
    ShowSlide(init = false, slicesex = null){
        let slices = this.GetSliceValue();
        if(slicesex != null){
            slices = slicesex;
        }
        if(!this.m_slave){
            let eventup = new CustomEvent("slidechange", { detail: {slices: slices} });
            this.m_parent.dispatchEvent(eventup);    
        }

        let config = this.GetConfig();        
        if(this.m_dimension == 1){
            let range = this.GetRanges(config);
            if(init){
                if(this.m_layout == null){
                    this.m_layout = GetLayout1D(this.m_axtitles, range.linear, range.log, config.xyscale);
                }
            }
            let variables = [];
            for(let n = 0; n < this.m_vardata.length; n++){
                variables.push(this.m_vardata[n][0]);
            }
            this.Plot1DAmination(this.m_id, this.m_layout, this.m_vardata.length, 
                variables, this.m_data, this.m_animlegend, this.m_compdata, slices);
        }
        else{
            this.Plot2DAnimation(this.m_id, 
                this.m_layout, this.m_vardata, this.m_data, slices, config, this.m_animlegend);
        }
    }

    SwitchAnimationButton(ison){
        this.m_animbtn.innerHTML = ison ? "&#9646;" : "&#9654;";
        if(ison){
            this.m_animintrv.setAttribute("disabled", "disabled");
        }
        else{
            this.m_animintrv.removeAttribute("disabled");
        }
    }

    SetupRelayout(id){
        let plyobj = document.getElementById(id);
        plyobj.on("plotly_relayout", (e) => {
            if(this.m_onrelayout){
                this.m_onrelayout = false;
                return;
            }
            let plobj = document.getElementById(id);
            let keys = Object.keys(e);
            if(keys.length == 0){
                return;
            }
            if(this.m_dimension == 1){
                keys.forEach((el) => {
                    if(el.includes("yaxis.range")){
                        this.m_ploptions[PlotOptionsLabel.yauto[0]] = false;
                    }
                });
                return;
            }
            if(this.m_dimension == 2){
                let layout = {};
                if(keys[0].indexOf("dragmode") >= 0){
                    let dmode = e["scene.dragmode"];
                    for(let j = 0; j < keys.length; j++){
                        layout[keys[j]] = dmode;
                    }
                }
                else if(keys[0].indexOf("range[0]") >= 0){
                    let vranges = ["", "", "", ""];
                    let xylabels = ["xaxis", "xaxis", "yaxis", "yaxis"];
                    let rlabels = [".range[0]", ".range[1]", ".range[0]", ".range[1]"];
                    let ixy, iif;
                    for(let j = 0; j < keys.length; j++){
                        if(keys[j].indexOf("xaxis") >= 0){
                            ixy = 0;
                        }
                        else if(keys[j].indexOf("yaxis") >= 0){
                            ixy = 1;
                        }
                        else{
                            continue;
                        }
                        if(keys[j].indexOf("[0]") >= 0){
                            iif = 0;
                        }
                        else if(keys[j].indexOf("[1]") >= 0){
                            iif = 1;
                        }
                        else{
                            continue;
                        }
                        vranges[2*ixy+iif] = e[keys[j]];
                    }
                    for(let j = 0; j < this.m_nplots; j++){
                        let numstr = j == 0 ? "" : (j+1).toString();
                        let xylabels = ["xaxis"+numstr, "yaxis"+numstr];
                        for(let k = 0; k < 2; k++){
                            layout[xylabels[k]] = CopyJSON(plobj.layout[xylabels[k]]);
                        }
                        for(let i = 0; i < 4; i++){
                            if(typeof vranges[i] != "number"){
                                continue;
                            }
                            if(i < 2){
                                layout[xylabels[0]].range[i] = vranges[i];
                            }
                            else{
                                layout[xylabels[1]].range[i-2] = vranges[i];
                            }
                        }
                    }
                }
                else if(keys[0].indexOf("camera") >= 0){
                    layout = CopyJSON(plobj.layout);
                    let camobj = e[keys[0]];
                    for(let n = 0; n < this.m_nplots; n++){
                        let label = GetSceneName(n);
                        layout[label].camera = CopyJSON(camobj);
                    }
                }
                let config = this.GetConfig();
                Object.keys(layout).forEach((el) => {
                    this.m_layout[config.type2d][el] = CopyJSON(layout[el]);
                });
                this.m_onrelayout = true;
                Plotly.relayout(id, this.m_layout[config.type2d]);
            }
        });
    }

    ExportPlotWindow(id, path = ""){
        let data = this.GetASCIIData();
        ExportAsciiData(data, id, path);
    }

    GetASCIIData()
    {
        let plobj = document.getElementById(this.m_id);
        let data = GetAsciiData(this.m_dimension, plobj);
        return data;
    }
}

class DataObject {
    constructor(categtitles, datapath){
        this.m_dataname = GetDataname(datapath);
        this.m_datapath = datapath;
        this.m_dataconts = {};
        this.m_categories = [];
        this.m_categtitles  = categtitles;
    }

    GetDataname(){
        return this.m_dataname;
    }

    GetInput(){
        return this.m_input;            
    }

    GetExprms(){
        return this.m_exprms;
    }

    GetSpec(spec, categ){
        if(spec == "comment"){
            return this.m_comment;
        }
        else if(spec == "dataname"){
            return this.m_dataname;
        }
        return this.m_dataconts[categ][spec];
    }

    GetCategory(){
        return this.m_categories;
    }

    LoadFile(fileobj){
        let dataobjs = [], categs = [];
        this.m_input = fileobj[InputLabel];

        this.m_comment = "";
/*


        empty space


*/
        if(fileobj.hasOwnProperty(ElapsedTimeLabel)){
            let etobj = CopyJSON(fileobj[ElapsedTimeLabel]);
            this.m_comment = etobj;
        }
        if(this.m_input[OutFileLabel].hasOwnProperty(OutputOptionsLabel.comment[0])){
            let comment = this.m_input[OutFileLabel][OutputOptionsLabel.comment[0]];
            if(comment != ""){
                this.m_comment[OutputOptionsLabel.comment[0]] = comment;
            }
        }

        if(fileobj.hasOwnProperty(PostPResultLabel)){
            let serno = this.m_input[PostPLabel][PostProcessPrmLabel.serialpp[0]];
            let category = PostPResultLabel;
            if(serno >= 0){
                category += " "+serno.toString();
            }
            category += ": "+this.m_input[PostPLabel][PostProcessPrmLabel.item[0]];
            categs.push(category);
            dataobjs.push(fileobj[PostPResultLabel]);

            let fidx = this.m_categories.indexOf(category);
            if(fidx >= 0){
                this.m_categories.splice(fidx, 1);
            }
        }
        else{
            for(let j = 0; j < this.m_categtitles.length; j++){
                delete this.m_dataconts[this.m_categtitles[j]];
                let fidx = this.m_categories.indexOf(this.m_categtitles[j]);
                if(fidx >= 0){
                    this.m_categories.splice(fidx, 1);
                }
                if(fileobj.hasOwnProperty(this.m_categtitles[j])){
                    categs.push(this.m_categtitles[j]);
                    dataobjs.push(fileobj[this.m_categtitles[j]]);
                }    
            }    
            if(fileobj.hasOwnProperty(CoordinateLabel)){
                this.m_exprms = fileobj[CoordinateLabel];
            }
            else{
                this.m_exprms = null;
            }
        }       
        for(let n = 0; n < dataobjs.length; n++){
            this.LoadData(dataobjs[n], categs[n]);
        }
        return categs[0];
    }

    LoadData(dataobj, category){
        let obj = {};
        obj.titles = dataobj[DataTitlesLabel];
        obj.units = dataobj[UnitsLabel];
        obj.dimension = dataobj[DataDimLabel];
        obj.link2d = false;
        if(dataobj.hasOwnProperty(Link2DLabel)){
            obj.link2d = dataobj[Link2DLabel];
        }
        obj.scatter = false;
        if(dataobj.hasOwnProperty(PlotScatterLabel)){
            obj.scatter = dataobj[PlotScatterLabel];
        }
        if(obj.scatter){
            obj.variables = 0;
            if(dataobj.hasOwnProperty(VariablesLabel)){
                obj.scans = dataobj[VariablesLabel];
            }
            else{
                obj.scans = 0;
            }
        }
        else if(dataobj.hasOwnProperty(VariablesLabel)){
            if(dataobj[VariablesLabel] == 0){
                obj.variables = dataobj[DataDimLabel];
                obj.scans = 0;
            }
            else{
                obj.variables = dataobj[VariablesLabel];
                obj.scans = dataobj[DataDimLabel]-dataobj[VariablesLabel];
            }
        }
        else{
            obj.variables = dataobj[DataDimLabel];
            obj.scans = 0;
        }
        if(dataobj.hasOwnProperty(DetailsLabel)){
            obj.details = dataobj[DetailsLabel];
        }
        else{
            obj.details = [];
        }
        obj.dataset = dataobj[DataLabel];

        this.m_categories.push(category);
        this.m_dataconts[category] = obj;
    }
}

class PostProcessor {
    constructor(datatype, plotdivid, categtitles, defaultlabel, selid = null, subid = null){
//        let panelwidth = "240px";
        this.m_panel = document.createElement("div");
        this.m_panel.className = "d-flex flex-column h-100";
//        this.m_panel.style.width = panelwidth;
        this.m_onrelayout = false;
        this.m_plotwindow = [];
        this.m_currid = null;
        this.m_subid = subid;
        this.m_zcurr = {};
        this.m_defaultlabel = defaultlabel;
        this.m_categcurrent = this.m_defaultlabel;
        this.m_categtitles = categtitles;
        this.m_plotid = plotdivid+"_plot";
        this.m_plotdivid = plotdivid;

        this.m_selects = {};
        this.m_checkboxes = {};
        this.m_labels = {};

        this.m_outfiles = document.createElement("select");
        this.m_outfiles.addEventListener("change", 
            (e) => {
                this.ChangeDataname(e.currentTarget.value);
            });
        this.m_selects.dataname = this.m_outfiles;
        
        this.m_categlabel = document.createElement("div");
        this.m_categlabel.innerHTML = "Data Type";
        this.m_categlabel.className = "d-none mt-1 mb-0";
        this.m_category = document.createElement("select");
        this.m_category.addEventListener("change", 
            (e) => {
                this.SetupCurrent();
            });
        this.m_category.className = "d-none";
        this.m_selects.datatype = this.m_category;
        
        this.m_comcaptions = document.createElement("div");
        this.m_comcaptions.style.width = "100%";
        this.m_comcaptions.style.whiteSpace = "normal";
        this.m_comcaptions.style.margin = "0 0 10px 0";
        this.m_comcaptions.className = "mt-1 lh-1"
//        this.m_comcaptions.style.overflow = "auto";
        this.m_framecurr = [0, 0];
        this.m_currztitles = "";
        this.m_objnames = [];
        this.m_dataobjs = [];
        this.m_rawresults = [];
        this.m_allids = [];

        this.m_fdialog = CreateFileDialogElement(datatype, "Import", true, true);
        this.m_fdialog.file.id = "file-postproc";
        this.m_fdialog.button.addEventListener("click",
            async (e) => {
                if(Framework == TauriLabel){
                    let paths = await GetPathDialog(
                        "Select output files", "postproc", true, true, true, true);
                    if(paths == null){
                        return;
                    }
                    SwitchSpinner(true);
                    for(let n = 0; n < paths.length; n++){
                        let data = await window.__TAURI__.tauri.invoke("read_file", { path: paths[n]});
                        this.LoadOutputFile(data, paths[n], n == paths.length-1);
                    }
                }
                else if(Framework == PythonGUILabel){
                    let id = [MenuLabels.postproc, MenuLabels.import].join(IDSeparator);
                    PyQue.Put(id);
                }
                else{
                    this.m_fdialog.file.click();
                }
            });
        this.m_fdialog.file.addEventListener("change",
            (e) => {
                LoadFiles(e, this.LoadOutputFile.bind(this));
            });

        this.m_buttons = {};

        let dlbtn = null;        
        if(Framework == ServerLabel){
            dlbtn = document.createElement("button");
            dlbtn.className = "btn btn-outline-primary btn-sm";
            dlbtn.addEventListener("click",
                (e) => {
                    let currdata = GetSelections(this.m_outfiles).value[0];                
                    this.Download(currdata);
                });
            this.m_buttons.dload = dlbtn;    
        }

        let clrbtn = document.createElement("button");
        clrbtn.className = "btn btn-primary btn-sm";
        clrbtn.addEventListener("click",
            (e) => {
                this.ClearData();
            });
        this.m_buttons.clear = clrbtn;

        let rmbtn = document.createElement("button");
        rmbtn.className = "btn btn-primary btn-sm me-1";
        rmbtn.addEventListener("click",
            (e) => {
                let currdata = GetSelections(this.m_outfiles).value[0];                
                this.RemoveData(currdata);
            });
        this.m_buttons.remove = rmbtn;

        let fdiv = document.createElement("div");
        fdiv.className = "d-flex align-items-end";
        this.m_fdialog.body.classList.add("flex-grow-1");

        if(dlbtn != null){
            fdiv.appendChild(dlbtn);
        }
        fdiv.appendChild(this.m_fdialog.body);
        fdiv.appendChild(rmbtn);
        fdiv.appendChild(clrbtn);

        if(selid != null){
            document.getElementById(selid).appendChild(fdiv);
            document.getElementById(selid).appendChild(this.m_outfiles);
        }
        else{
            this.m_panel.appendChild(fdiv);
            this.m_panel.appendChild(this.m_outfiles);
        }
      
        this.m_subpanels = document.createElement("div");
        this.m_subpanels.className = "d-none flex-column h-100";
        this.m_panel.appendChild(this.m_subpanels);

        this.CreateSubpanel();
    
        this.m_btnids = {};
        Object.keys(this.m_buttons).forEach(btn => {
            this.m_btnids[MenuLabels[btn]] = [MenuLabels.postproc, MenuLabels[btn]].join(IDSeparator);
            this.m_buttons[btn].innerHTML = MenuLabels[btn];
            this.m_buttons[btn].id = this.m_btnids[MenuLabels[btn]];
        });

        this.m_selectids = {};
        Object.keys(this.m_selects).forEach(sel => {
            this.m_selectids[MenuLabels[sel]] = "postproc-sel-"+sel;
            this.m_selects[sel].id = this.m_selectids[MenuLabels[sel]];
        });

        this.m_checkids = {};
        Object.keys(this.m_checkboxes).forEach(chk => {
            this.m_checkids[MenuLabels[chk]] = "postproc-chk-"+chk;
            this.m_checkboxes[chk].id = this.m_checkids[MenuLabels[chk]];
            this.m_labels[chk].setAttribute("for", this.m_checkids[MenuLabels[chk]]);
        });
        document.getElementById("runpostp").innerHTML = MenuLabels.runpostp;
    }

    DisableRun()
    {
        document.getElementById("runpostp").classList.add("d-none");
    }

    GetCurrentDataName()
    {
        let selections = GetSelections(this.m_outfiles);
        if(selections.value.length == 0){
            return "";
        }
        return selections.value[0];
    }

    Import(){
        this.m_fdialog.button.click();
    }

    Click(btn)
    {
        if(this.m_buttons.hasOwnProperty(btn)){
            this.m_buttons[btn].click();
        }
        else if(this.m_btnids.hasOwnProperty(btn)){
            document.getElementById(this.m_btnids[btn]).click();
        }
        else{
            if(document.getElementById(btn)){
                document.getElementById(btn).click();
            }
        }
    }

    HideDLButton()
    {
        if(Framework != ServerLabel && this.m_buttons.hasOwnProperty("dload")){
            this.m_buttons.dload.classList.add("d-none");
        }
    }

    GetASCIIData(){
        let data = new Array(this.m_plotwindow.length);
        for(let n = 0; n < this.m_plotwindow.length; n++){
            data[n] = this.m_plotwindow[n].GetASCIIData();
        }
        return data;
    }

    GetWholeObject(isascii = false){
        let obj = GetPlotObj(this.GetPanelSize(), this.m_plotwindow, true);
        if(isascii){
            return obj.data[0].data;
        }
        return obj;
    }

    GetSelectID(target)
    {
        let id = "";
        if(this.m_selects.hasOwnProperty(target)){
            id = this.m_selects[target].id;
        }
        if(this.m_selectids.hasOwnProperty(target)){
            id = this.m_btnids[btn];
        }
        return id;
    }

    GetCheckID(target)
    {
        let id = "";
        if(this.m_checkboxes.hasOwnProperty(target)){
            id = this.m_checkboxes[target].id;
        }
        if(this.m_checkids.hasOwnProperty(target)){
            id = this.m_checkids[btn];
        }
        return id;
    }

    GetColumnsID(issub = true){
        if(issub){
            return this.m_subplotcols.id;
        }
        return this.m_plotcols.id;
    }

    ChangePlotOptions(changes){
        for(const plot of this.m_plotwindow){
            plot.ChangeOptionDirect(changes);
        }
    }

    GetPlotCols()
    {
        return parseInt(this.m_plotcols.value); 
    }

    GetSubPlotCols()
    {
        return parseInt(this.m_subplotcols.value); 
    }

    Count(){
        return this.m_objnames.length;
    }

    EnableSubPanel(enable)
    {
        if(enable){
            this.m_subpanels.classList.replace("d-none", "d-flex");
        }
        else{
            this.m_subpanels.classList.replace("d-flex", "d-none");
        }
    }

    GetPanelSize()
    {
        return GetPlotPanelSize(this.m_plotdivid);
    }

    SetPlotCols(value)
    {
        this.m_plotcols.value = value;
    }

    SetSubPlotCols(value)
    {
        this.m_subplotcols.value = value;
    }

    CreateSubpanel()
    {
        this.m_subpanels.appendChild(this.m_categlabel);
        this.m_subpanels.appendChild(this.m_category);
        this.m_subpanels.appendChild(this.m_comcaptions);    

        let selbox = CreateSelectBox("x axis", 1, false, true);
        this.m_xdiv = selbox.body;
        this.m_xaxis = selbox.select;
        this.m_selects.xaxis = this.m_xaxis;

        selbox = CreateSelectBox("x-y axis", 1, false, true);
        this.m_xydiv = selbox.body;
        this.m_xyaxis = selbox.select;
        this.m_selects.xyaxis = this.m_xyaxis;
        
        selbox = CreateSelectBox("Items to Plot", 5, true, true);
        this.m_zdiv = selbox.body;
        this.m_zaxis = selbox.select;
        this.m_selects.item = this.m_zaxis;

        this.m_expotbtn = document.createElement("button");
        this.m_expotbtn.className = "d-none btn btn-outline-primary btn-sm";
        this.m_expotbtn.addEventListener("click", async (e) => {
            let id = [MenuLabels.postproc, MenuLabels.ascii].join(IDSeparator)
            if(Framework == PythonGUILabel){
                PyQue.Put(id);
                return;
            }        
            ExportPlotWindows(id, this.m_plotwindow);
        });
        this.m_buttons.ascii = this.m_expotbtn;

        this.m_savebtn = document.createElement("button");
        this.m_savebtn.className = "d-none btn btn-outline-primary btn-sm";
        this.m_savebtn.addEventListener("click", (e)=>{
            if(Framework == PythonGUILabel){
                let id = [MenuLabels.postproc, MenuLabels.save].join(IDSeparator);
                PyQue.Put(id);
                return;
            }
            let plobj = this.GetWholeObject();
            let dataname = this.GetCurrentDataName();
            SavePlotObj(plobj, dataname);
        });
        this.m_buttons.save = this.m_savebtn;

        this.m_newwinbtn = document.createElement("button");
        this.m_newwinbtn.className = "d-none btn btn-primary btn-sm";
        this.m_newwinbtn.addEventListener("click", (e)=>{
            this.DuplicatePlot();
        });
        this.m_buttons.duplicate = this.m_newwinbtn;

        this.m_xdiv.classList.replace("d-flex", "d-none");
        this.m_xydiv.classList.replace("d-flex", "d-none");
        this.m_zdiv.classList.replace("d-flex", "d-none");

        this.m_subpanels.appendChild(this.m_xdiv);
        this.m_subpanels.appendChild(this.m_xydiv);
        this.m_subpanels.appendChild(this.m_zdiv);

        this.m_compenable = false;
        this.m_compdiv = document.createElement("div");
        this.m_compdiv.className = "d-none flex-column";
        this.m_subpanels.appendChild(this.m_compdiv);

        let space = document.createElement("div");
        space.className = "flex-grow-1";
        let btndiv = document.createElement("div");
        btndiv.className = "btn-group";
        btndiv.appendChild(this.m_expotbtn);
        btndiv.appendChild(this.m_savebtn);
        btndiv.appendChild(this.m_newwinbtn);
        this.m_subpanels.appendChild(space);
        this.m_subpanels.appendChild(btndiv);

        let chk = CreateCheckBox(MenuLabels.comparative, false, "comparative_check");
        this.m_compchkbox = chk.chkbox;
        this.m_compchkbox.addEventListener("click", (e) => {
            this.CheckComparable(e.currentTarget.checked);
        });
        this.m_checkboxes.comparative = this.m_compchkbox;
        this.m_labels.comparative = chk.label;

        selbox = CreateSelectBox("Data Available", 5, true, true);
        this.m_complist = selbox.select;
        this.m_complist.className = "d-none";
        this.m_compdiv.appendChild(chk.div);
        this.m_compdiv.appendChild(this.m_complist);
        this.m_selects.comparative = this.m_complist;

        let subplotcol = CreateNumberInput(SubPlotsRowLabel, [1, 1, 4], "subplotcols");
        this.m_subplotcols = subplotcol.input;
        this.m_subplotcols.value = 2;
        this.m_subplotcoldiv = subplotcol.div;
        this.m_subplotcoldiv.classList.add("mt-1");
        this.m_subplotcoldiv.classList.add("mb-1");
        this.m_subplotcoldiv.classList.add("d-none");
        this.m_subplotcols.addEventListener("change", (e) => {
            this.PlotCurrentResult();
        });       
        this.m_compdiv.appendChild(subplotcol.div);

        let hr = document.createElement("hr");
        this.m_compdiv.appendChild(hr);

        this.m_mplotenable = false;
        let chkmlp = CreateCheckBox(MenuLabels.multiplot, false, "multi_check");
        this.m_mplotchkbox = chkmlp.chkbox;
        this.m_mplotchkbox.addEventListener("click", (e) => {
            this.CheckMultiplot(e.currentTarget.checked);
        });
        this.m_checkboxes.multiplot = this.m_mplotchkbox;
        this.m_labels.multiplot = chkmlp.label;

        selbox = CreateSelectBox("Data Available", 5, true, true);
        this.m_mplotlist = selbox.select;
        this.m_mplotlist.className = "d-none";
        this.m_compdiv.appendChild(chkmlp.div);
        this.m_compdiv.appendChild(this.m_mplotlist);
        this.m_selects.multiplot = this.m_mplotlist;

        let plotcol = CreateNumberInput(PlotWindowsRowLabel, [1, 1, 4], "plotcols");
        this.m_plotcols = plotcol.input;
        this.m_plotcols.value = 2;
        this.m_plotcoldiv = plotcol.div;
        this.m_plotcoldiv.classList.add("mt-1");
        this.m_plotcoldiv.classList.add("mb-1");
        this.m_plotcoldiv.classList.add("d-none");
        this.m_plotcols.addEventListener("change", (e) => {
            this.PlotCurrentResult();
        });       
        this.m_compdiv.appendChild(plotcol.div);

        this.m_xaxis.addEventListener("change", 
            (e) => {
                this.PlotCurrentResult();
            });

        this.m_xyaxis.addEventListener("change", 
            (e) => {
                this.ArrangeComparative();
                this.PlotCurrentResult();
            });
           
        this.m_zaxis.addEventListener("change", 
            (e) => {
                this.ArrangeComparative();
                this.PlotCurrentResult();
            });

        this.m_complist.addEventListener("change", 
            (e) => {
                this.PlotCurrentResult();
            });

        this.m_mplotlist.addEventListener("change", 
            (e) => {
                this.PlotCurrentResult();
            });            
    }

    DuplicatePlot(titles = []){
        let plotobj = GetPlotObj(this.GetPanelSize(), this.m_plotwindow, true);
        for(let j = 0; j < plotobj.data.length; j++){
            if(j >= titles.length){
                plotobj.data[j].title = "";
            }
            else{
                plotobj.data[j].title = titles[j];
            }
        }
        CreateNewplot(plotobj);
    }

    SetupCurrent()
    {
        this.SetIndex();
        this.SaveFormerSettings();
        this.ShowItems();
        this.m_categcurrent = GetSelections(this.m_category).value[0];
    }

    ChangeDataname(value)
    {
        if(this.m_subpanels.classList.contains("d-flex")){
            this.SetCategories(value);
            this.SetupCurrent();
        }

        let exprms = null, input = null;
        let objindex = this.m_objnames.indexOf(value);
        if(objindex >= 0){
            exprms = this.m_dataobjs[objindex].GetExprms();
            input = this.m_dataobjs[objindex].GetInput();
        }
        if(input != null && exprms != null){
            GUIConf.GUIpanels[PostPLabel].SetInput(input, exprms);
        }
    }

    SetIndex(){
        if(this.m_outfiles.selectedIndex == -1 || this.m_category.selectedIndex == -1){
            this.m_currid = null;
            return;
        }
        this.m_currid = [GetSelections(this.m_outfiles).value[0], 
            GetSelections(this.m_category).value[0]].join(IDSeparator);
    }

    CheckComparable(checked, isclear = false){
        this.m_compenable = checked;
        if(this.m_compenable){
            this.m_complist.classList.remove("d-none");
        }
        else{
            this.m_complist.classList.add("d-none");
        }
        if(isclear){
            return;
        }
        this.CheckPlotCols();
        this.PlotCurrentResult();
    }

    CheckMultiplot(checked, isclear = false){
        this.m_mplotenable = checked;
        if(this.m_mplotenable){
            this.m_mplotlist.classList.remove("d-none");
        }
        else{
            this.m_mplotlist.classList.add("d-none");
        }
        if(isclear){
            return;
        }
        this.CheckPlotCols();
        this.PlotCurrentResult();
    }

    CheckPlotCols()
    {
        if(this.m_compenable || this.m_mplotenable){
            this.m_plotcoldiv.classList.remove("d-none");
        }
        else{
            this.m_plotcoldiv.classList.add("d-none");
        }
    }

    Refresh(){
        for(let n = 0; n < this.m_plotwindow.length; n++){
            this.m_plotwindow[n].RefreshPlotObject();
        }
    }

    GetPanel(){
        return this.m_panel;
    }

    GetSpec(spec, id, isshort = false){
        let ids = id.split(IDSeparator);
        let index = this.m_objnames.indexOf(ids[0]);
        let categ = ids[1];
        let result = this.m_dataobjs[index].GetSpec(spec, categ);
        if(isshort){
            result = this.ConvertShort(result);
        }
        return result;
    }
    
    ConvertShort(titles){
        let labels = Object.keys(ShortTitles);
        let stitles = Array.from(titles);
        for(let j = 0; j < stitles.length; j++){
            if(labels.includes(stitles[j])){
                stitles[j] = ShortTitles[stitles[j]];
            }
        }
        return stitles;
    }

    GetCategory(id){
        return id.split(IDSeparator)[1];
    }

    SetAllIndices(){
        this.m_allids = [];
        for(let n = 0; n < this.m_dataobjs.length; n++){
            let dataname = this.m_dataobjs[n].GetDataname();
            let categories = this.m_dataobjs[n].GetCategory();
            for(let j = 0; j < categories.length; j++){
                this.m_allids.push([dataname, categories[j]].join(IDSeparator));
            }
        }
    }

    DeleteOutputFile(dataname)
    {
        let options = this.m_outfiles.options;
        for(let n = options.length-1; n >= 0; n--){
            if(options[n].value == dataname){
                this.m_outfiles.remove(n);
            }
        }
    }

    AbortLoad(isfinal){
        if(isfinal){
            SwitchSpinner(false);            
        }
    }

    LoadOutputFile(result, datapath, isfinal){
        let fileobj;
        try{
            fileobj = JSON.parse(result);
        }
        catch (e){
            Alert("Error: invalid format.\n"+e.message);
            this.AbortLoad(isfinal);
            if(isfinal){
                GUIConf.loading = false;
            }
            return;
        }
        let objindex = this.LoadObject(fileobj, datapath, isfinal);
        if(Framework == ServerLabel && objindex >= 0){
            if(objindex >= this.m_rawresults){
                this.m_rawresults.push(result);
            }
            else{
                this.m_rawresults[objindex] = result;
            }
        }
        if(isfinal){
            GUIConf.loading = false;
        }
    }

    LoadObject(fileobj, datapath, isfinal)
    {
        if(!fileobj.hasOwnProperty(InputLabel)){
            if(!fileobj.hasOwnProperty(ScanLabel)){
                Alert("Error: cannot load the input parameters.");
            }
            this.AbortLoad(isfinal);
            return -1;
        }

        if(fileobj.hasOwnProperty(PostPResultLabel)){
            if(!fileobj[InputLabel].hasOwnProperty(DataNameLabel)){
                Alert("Error: data file name for post-processing not found.");
                this.AbortLoad(isfinal);
                return -1;    
            }
            datapath = fileobj[InputLabel][DataNameLabel];        
        }
        let dataname = GetDataname(datapath);
        let objindex = this.m_objnames.indexOf(dataname);
        if(objindex < 0){
            this.m_dataobjs.push(new DataObject(this.m_categtitles, datapath));
            this.m_objnames.push(dataname);
            objindex = this.m_dataobjs.length-1;

            let option = document.createElement("option");
            option.text = dataname;
            option.value = dataname;
            this.m_outfiles.appendChild(option);    
        }
        let categ = this.m_dataobjs[objindex].LoadFile(fileobj);
        
        if(isfinal){
            document.getElementById("viewresult").classList.replace("d-none", "d-flex");
            this.m_fdialog.file.value = "";
            this.SetCategories(dataname);
            SetSelectedItem(this.m_outfiles, dataname);
            SetSelectedItem(this.m_category, categ);
            this.m_currid = [dataname, categ].join(IDSeparator);
            this.SetAllIndices();
            this.ShowItems();
            SwitchSpinner(false);
        }
        return objindex;
    }

    Download(value)
    {
        let idx = this.m_objnames.indexOf(value);
        if(idx < 0){
            return;
        }
        ExportAsciiData(this.m_rawresults[idx], null, this.m_objnames[idx], true);
    }

    RemoveData(value)
    {
        let idx = this.m_objnames.indexOf(value);
        if(idx < 0){
            return;
        }
        this.m_objnames.splice(idx, 1);
        this.m_dataobjs.splice(idx, 1);
        if(Framework == ServerLabel){
            this.m_rawresults.splice(idx, 1);
        }
        this.DeleteOutputFile(value);
        for(let n = this.m_allids.length-1; n >= 0; n--){
            if(this.m_allids[n].split(IDSeparator)[0] == value){
                this.m_allids.splice(n, 1);
            }
        }
        if(this.m_objnames.length == 0){
            this.ClearData();
        }
        else{
            SetSelection(this.m_outfiles, this.m_objnames[0], false);
            this.ChangeDataname(this.m_objnames[0]);
        }
    }

    ClearData(){
        this.m_objnames.length = 0;
        this.m_dataobjs.length = 0;
        if(Framework == ServerLabel){
            this.m_rawresults.length = 0;
        }
        this.m_allids.length = 0;

        this.m_outfiles.innerHTML = "";
        this.m_comcaptions.innerHTML = "";
        this.m_xcurr = "";
        this.m_xycurr = "";
        this.m_zcurr = {};
        this.m_categcurrent = this.m_defaultlabel;
        this.m_compenable = false;
        this.m_compchkbox.checked = false;
        this.CheckComparable(false, true);

        this.m_mplotenable = false;
        this.m_mplotchkbox.checked = false;
        this.CheckMultiplot(false, true);

        this.m_plotcoldiv.classList.add("d-none");
        this.m_category.classList.add("d-none");
        this.m_categlabel.classList.add("d-none");
        this.m_xdiv.classList.replace("d-flex", "d-none");
        this.m_xydiv.classList.replace("d-flex", "d-none");
        this.m_zdiv.classList.replace("d-flex", "d-none");
        this.m_compdiv.classList.replace("d-flex", "d-none");
        this.m_expotbtn.classList.add("d-none");
        this.m_savebtn.classList.add("d-none");
        this.m_newwinbtn.classList.add("d-none");
        document.getElementById("viewresult").classList.replace("d-flex", "d-none");
                
        this.m_currid = null;
        this.ShowItems();

        let pp_plot = document.getElementById(this.m_plotdivid);
        pp_plot.innerHTML = "";
        this.m_plotwindow = [];

        if(this.m_subid != null){
            document.getElementById(this.m_subid).classList.add("d-none");
        }
    }

    GetPlotConfig(id){
        let dims = this.GetSpec("scans", id)+this.GetSpec("variables", id);
        let link2d = this.GetSpec("link2d", id);
        if(this.GetSpec("scatter", id)){
            this.m_plotdims = [];
        }
        else if(this.GetSpec("details", id).length > 0){
            // plot x: variable, frame: scan
            if(dims == 2){
                this.m_plotdims = [
                    [[0], [1]],
                    // skip [[1], [0]] to avoid discrepancy in # variables
                    [[0, 1], []]
                ];
            }
            else if(dims == 3){
                this.m_plotdims = [
                    [[0], [1, 2]]
                ];
            }
            else{
                this.m_plotdims = [];
            }
        }
        else if(dims == 0 || dims > 4){
            this.m_plotdims = [];
            return false;
        }
        else if(dims == 4){
            this.m_plotdims = PPFormats.idxpair4d;
            if(link2d){
                this.m_plotdims = [
                    [[0, 1], [2, 3]]
                ];
            }
        }
        else if(dims == 3){
            this.m_plotdims = PPFormats.idxpair3d;
            if(link2d){
                this.m_plotdims = [
                    [[0], [1, 2]]
                ];
            }
        }
        else if(dims == 2){
            if(this.GetSpec("scans", id) == 0){
                this.m_plotdims = [
                    [[0, 1], []]
                ];
            }
            else{
                this.m_plotdims = PPFormats.idxpair2d;
            }
        }
        else{
            this.m_plotdims = [];
        }
        return true;
    }

    ShowItems(){
        this.m_xaxis.innerHTML = "";
        this.m_xyaxis.innerHTML = "";
        this.m_zaxis.innerHTML = "";
        this.m_complist.innerHTML = "";
        this.m_mplotlist.innerHTML = "";
        if(this.m_currid == null){
            return;
        }

        this.m_comcaptions.innerHTML = "";
        let comment = this.GetSpec("comment", this.m_currid);
        if(typeof comment == "object"){
            let keys = Object.keys(comment);
            for(let j = 0; j < keys.length; j++){
                let cont = document.createElement("div");

                let comobj = comment[keys[j]];
                if(Array.isArray(comobj)){
                    if(comobj.length > 2){
                        let tmpobj = [];
                        for(let i = 0; i < 2; i++){
                            tmpobj.push(comobj[i].toString());
                        }
                        tmpobj.push("...");
                        comobj = tmpobj.join(",");
                    }
                }
                cont.innerHTML = keys[j]+": "+comobj;
                this.m_comcaptions.appendChild(cont);
            }
        }
        else if(comment != ""){
            this.m_comcaptions.innerHTML = "\""+comment+"\"";
        }

        if(!this.GetPlotConfig(this.m_currid)){
            return;
        }

        let items = this.GetSpec("titles", this.m_currid);
        if(this.m_plotdims.length > 0){
            for(let i = 0; i < this.m_plotdims.length; i++){
                let option = document.createElement("option");
                if(this.m_plotdims[i].length == 0){
                    continue;
                }
                else if(this.m_plotdims[i][0].length == 1){
                    option.text = items[this.m_plotdims[i][0][0]];
                }
                else{
                    option.text = "("+items[this.m_plotdims[i][0][0]]+", "+items[this.m_plotdims[i][0][1]]+")";
                }
                option.value = option.text;
                this.m_xyaxis.appendChild(option);
            }   
            this.m_xydiv.classList.replace("d-none", "d-flex");
        }
        else{
            this.m_xydiv.classList.replace("d-flex", "d-none");
        }
        this.SetTargetItems(this.m_currid);
        this.RestoreFormerSettings();
        this.ArrangeComparative();
        if(this.m_subpanels.classList.contains("d-flex")){
            this.PlotCurrentResult();
        }

        let exprms = null, input = null;
        let objindex = this.m_objnames.indexOf(this.GetSpec("dataname", this.m_currid));
        if(objindex >= 0){
            exprms = this.m_dataobjs[objindex].GetExprms();
            input = this.m_dataobjs[objindex].GetInput();
        }

        if(input != null && exprms != null){
            GUIConf.GUIpanels[PostPLabel].SetInput(input, exprms);
        }
        if(this.m_subid != null){
            if(input != null && exprms != null){
                document.getElementById(this.m_subid).classList.remove("d-none");
            }
            else{
                document.getElementById(this.m_subid).classList.add("d-none");
            }
        }
    }

    SaveFormerSettings(){
        this.m_xcurr = "";
        this.m_xycurr = "";
        this.m_framecurr = [0, 0];
        if(this.m_xdiv.classList.contains("d-flex")){
            this.m_xcurr = GetSelections(this.m_xaxis).value[0];
        }
        if(this.m_xydiv.classList.contains("d-flex")){
            this.m_xycurr = GetSelections(this.m_xyaxis).value[0];            
        }
        if(this.m_zdiv.classList.contains("d-flex")){
            this.m_zcurr[this.m_categcurrent] = GetSelections(this.m_zaxis).value;
        }
    }

    RestoreFormerSettings(){
        if(this.m_xdiv.classList.contains("d-flex") && this.m_xcurr != ""){
            SetSelection(this.m_xaxis, this.m_xcurr, false);
        }
        if(this.m_xydiv.classList.contains("d-flex") && this.m_xycurr != ""){
            SetSelection(this.m_xyaxis, this.m_xycurr, false);
        }
        if(this.m_zdiv.classList.contains("d-flex")){
            let category = GetSelections(this.m_category).value[0];
            if(this.m_zcurr.hasOwnProperty(category)){
                SetSelection(this.m_zaxis, this.m_zcurr[category], false);
            }
        }
    }

    SetCategories(dataname){
        let objindex = this.m_objnames.indexOf(dataname);        
        let categs = [];
        if(objindex >= 0){
            categs = this.m_dataobjs[objindex].GetCategory();
        }
        let selidx = this.m_categcurrent;
        if(categs.indexOf(selidx) < 0){
            selidx = categs[0];
        }
        SetSelectMenus(this.m_category, categs, [], selidx);
        if(categs.length <= 1){
            this.m_category.classList.add("d-none");
            this.m_categlabel.classList.add("d-none");            
        }
        else{
            this.m_category.classList.remove("d-none");
            this.m_categlabel.classList.remove("d-none");            
        }
    }

    GetCurrentCategory(){
        if(this.m_categcurrent == this.m_defaultlabel){
            return ""
        }
        return this.m_categcurrent;
    }

    SetTargetItems(id){
        let dim = this.GetFrameConfig();
        if(dim == null){
            return;
        }
        let items = this.GetSpec("titles", id);
        if(dim.plot == 2){
            for(let i = this.GetSpec("dimension", id); i < items.length; i++){
                let option = document.createElement("option");
                option.text = items[i];
                option.value = items[i];
                this.m_zaxis.appendChild(option);
            }
            this.m_xdiv.classList.replace("d-flex", "d-none");
            this.m_zdiv.classList.replace("d-none", "d-flex");
            this.m_subplotcoldiv.classList.replace("d-none", "d-flex");
            this.m_zaxis.options[0].selected = true;
        }
        else{
            this.m_subplotcoldiv.classList.replace("d-flex", "d-none");
            if(this.m_xydiv.classList.contains("d-flex")){
                this.m_xdiv.classList.replace("d-flex", "d-none");
                for(let i = this.GetSpec("dimension", id); i < items.length; i++){
                    let option = document.createElement("option");
                    option.text = items[i];
                    option.value = items[i];
                    this.m_zaxis.appendChild(option);
                }
                this.m_zaxis.options[0].selected = true;
            }
            else{
                let fidx = -1, pidx = -1;
                this.m_xdiv.classList.replace("d-none", "d-flex");
                for(let i = 0; i < items.length; i++){
                    let option = document.createElement("option");
                    option.text = items[i];
                    option.value = items[i];
                    this.m_xaxis.appendChild(option);
                    option = document.createElement("option");
                    option.text = items[i];
                    option.value = items[i];
                    this.m_zaxis.appendChild(option);
                    if(fidx < 0 && items[i].indexOf("Flux") >= 0){
                        fidx = i;
                    }
                    if(pidx < 0 && items[i].indexOf("Power") >= 0){
                        pidx = i;
                    }
                }
                if(fidx >= 0){
                    this.m_zaxis.options[fidx].selected = true;
                }
                else if(pidx >= 0){
                    this.m_zaxis.options[pidx].selected = true;
                }
                else{
                    this.m_zaxis.options[this.GetSpec("dimension", id)].selected = true;
                }
            }
            this.m_zdiv.classList.replace("d-none", "d-flex");
        }
        if(this.GetSpec("scatter", id)){
            this.m_xdiv.classList.replace("d-flex", "d-none");
            this.m_xydiv.classList.replace("d-flex", "d-none");
            this.m_zdiv.classList.replace("d-flex", "d-none");
        }
        this.m_expotbtn.classList.remove("d-none");
        this.m_savebtn.classList.remove("d-none");        
        this.m_newwinbtn.classList.remove("d-none");
    }

    CheckSlideConsist(slideitems, id, frames)
    {
        for(let s = 0; s < slideitems.length; s++){
            if(this.GetSpec("titles", id).indexOf(slideitems[s]) < 0){
                return false;
            }
        }

        let dataset = new Array(2);
        let isslide = true;

        if(this.GetSpec("scans", this.m_currid) != this.GetSpec("scans", id)){
            isslide = false;
        }
        if(this.GetSpec("link2d", this.m_currid) != this.GetSpec("link2d", id)){
            isslide = false;
        }
        let variables = this.GetSpec("dimension", id)-slideitems.length;
        if(isslide && (variables > 2 || (variables <= 0 && this.GetSpec("scatter", id) == false))){
            isslide = false;
        }
        for(let j = 0; j < frames.length && isslide; j++){
            if(frames[j] < 0){
                continue;
            }
            if(this.GetSpec("details", this.m_currid).length > 0){
                dataset[0] = this.GetSpec("dataset", this.m_currid)[0];
            }
            else{
                dataset[0] = this.GetSpec("dataset", this.m_currid);
            }
            if(this.GetSpec("details", id).length > 0){
                dataset[1] = this.GetSpec("dataset", id)[0];
            }
            else{
                dataset[1] = this.GetSpec("dataset", id);
            }
            let frameno = this.GetSpec("titles", id).indexOf(this.GetSpec("titles", this.m_currid)[frames[j]]);
            if(frameno < 0){
                isslide = false;
                break;
            }
            if(dataset[0][frames[j]].length != dataset[1][frameno].length){
                isslide = false;
                break;
            }
        }
        return isslide;
    }

    ArrangeComparative(){
        let dim = this.GetFrameConfig();
        if(dim == null){
            return;
        }
        this.m_compdiv.classList.replace("d-none", "d-flex");

        this.SetIndex();
        let scatter = this.GetSpec("scatter", this.m_currid);

        let frames = [];
        if(scatter){
            for(let j = 0; j < this.GetSpec("scans", this.m_currid); j++){
                frames.push(j);
            }
        }
        else if(dim.xyidx >= 0){
            frames = CopyJSON(this.m_plotdims[dim.xyidx][1]);
        }

        let varitems = [];
        if(scatter){
            // do nothing
        }
        else if(dim.frame > 0){
            let plix = GetSelections(this.m_xyaxis).index[0];
            varitems.push(this.GetSpec("titles", this.m_currid)[this.m_plotdims[plix][0][0]]);
            if(this.m_plotdims[plix][0].length > 1){
                varitems.push(this.GetSpec("titles", this.m_currid)[this.m_plotdims[plix][0][1]]);    
            }
        }
        else if(this.GetSpec("dimension", this.m_currid) == 1){
            varitems.push(GetSelections(this.m_xaxis).value[0]);
            varitems = this.ConvertShort(varitems);
        }
        else{
            varitems.push(this.GetSpec("titles", this.m_currid)[0]);
            varitems.push(this.GetSpec("titles", this.m_currid)[1]);
        }

        let slideitems = this.GetSpec("titles", this.m_currid).slice(0, this.GetSpec("dimension", this.m_currid));
        for(let i = 0; i < varitems.length; i++){
            let sindex = slideitems.indexOf(varitems[i]);
            slideitems.splice(sindex, 1);
        }

        let plotitems = [];
        if(scatter){
            for(let j = this.GetSpec("scans", this.m_currid); j < this.GetSpec("titles", this.m_currid).length; j++){
                plotitems.push(this.GetSpec("titles", this.m_currid)[j]);
            }
        }
        else{
            plotitems = GetSelections(this.m_zaxis).value;
            plotitems = this.ConvertShort(plotitems);
        }

        this.m_comp_anims = [];
        this.m_comp_tgts = [];
        let mlplots = [];

        for(let i = 0; i < this.m_allids.length; i++){
            let id = this.m_allids[i];
            if(this.m_currid == id){
                continue;
            }

            // check slide variables
            let isslide = this.CheckSlideConsist(slideitems, id, frames);

            // check target items
            let isplot;
            if(scatter){
                isplot = true;
                for(let j = 0; j < plotitems.length; j++){
                    if(this.GetSpec("titles", id).indexOf(plotitems[j]) < 0){
                        isplot = false;
                        break;
                    }
                }    
            }
            else{
                isplot = false;
                for(let j = 0; j < plotitems.length; j++){
                    let titles = this.GetSpec("titles", id);
                    if(titles.indexOf(plotitems[j]) >= 0){
                        isplot = true;
                        break;
                    }
                }    
            }

            // check variables
            let isvar = true;
            for(let v = 0; v < varitems.length; v++){
                if(this.GetSpec("titles", id).indexOf(varitems[v]) < 0){
                    isvar = false;
                    break;
                }
            }

            if(isslide && isplot && isvar){
                this.m_comp_anims.push(id);
            }
            else if(isslide){
                let dim = this.GetSpec("dimension", id);
                let items = Array.from(this.GetSpec("titles", id));
                if(this.GetSpec("scatter", id)){
                    items.splice(0, dim+1);
                }
                else{
                    items.splice(0, dim);
                }
                mlplots.push({id:id, items:items});
            }
            else if(isplot && isvar && varitems.length == 1 && this.GetSpec("dimension", id) == 1){
                this.m_comp_tgts.push(id);
            }
        }

        let menuobj = [], valueobj = [];
        this.SetComparativeItems(menuobj, valueobj, this.m_comp_anims, false);
        this.SetComparativeItems(menuobj, valueobj, this.m_comp_tgts);
        SetSelectMenus(this.m_complist, menuobj, [], null, true, valueobj, MaxItems2Plot4PP);

        menuobj = [], valueobj = [];
        this.SetComparativeItems(menuobj, valueobj, mlplots);
        SetSelectMenus(this.m_mplotlist, menuobj, [], null, true, valueobj, MaxItems2Plot4PP);
    }

    SetComparativeItems(menuobj, valueobj, mlist, islast = true)
    {
        for(let i = 0; i < mlist.length; i++){
            let id;
            let isobj = typeof mlist[i] == "object";
            let subids = [];
            if(isobj){
                id = mlist[i].id;
                mlist[i].items.forEach(item => {
                    subids.push([id, item].join(IDSeparator));
                })
            }
            else{
                id = mlist[i];
            }
            let objidx  = -1;
            for(let j = 0; j < menuobj.length; j++){
                if(Object.keys(menuobj[j]).indexOf(this.GetSpec("dataname", id)) >= 0){
                    objidx = j;
                    break;
                }
            }
            let dataname = this.GetSpec("dataname", id);
            let categ = this.GetCategory(id);
            if(objidx >= 0){
                if(isobj){
                    menuobj[objidx][dataname].push({[categ]: mlist[i].items});
                    valueobj[objidx][dataname].push(subids);
                }
                else{
                    menuobj[objidx][dataname].push(categ);
                    valueobj[objidx][dataname].push(id);    
                }
            }
            else{
                if(isobj){
                    menuobj.push({[dataname]: [{[categ]: mlist[i].items}]});
                    valueobj.push({[dataname]: [subids]});
                }
                else{
                    menuobj.push({[dataname]: [categ]});
                    valueobj.push({[dataname]: [id]});
                }
            }
        }

        if(islast){
            for(let j = menuobj.length-1; j >= 0; j--){
                if(typeof menuobj[j] == "object"){
                    let dataname = Object.keys(menuobj[j])[0];
                    let irep = 0;
                    for(let k = 1; k < menuobj[j][dataname].length; k++){
                        let obj = menuobj[j][dataname][k];
                        if(typeof obj != "object"){
                            continue;
                        }
                        irep++;

                        let subname = Object.keys(obj)[0];                        
                        let subvalue = obj[subname];
                        let newname = [dataname, subname].join(IDSeparator);
                        let newobj = {};
                        newobj[newname] = [
                            {
                                [this.m_defaultlabel]:subvalue
                            }
                        ];
                        menuobj.splice(j+irep, 0, newobj);

                        let newval = {};
                        newval[newname] = [valueobj[j][dataname][k]];
                        valueobj.splice(j+irep, 0, newval);

                        menuobj[j][dataname].splice(k, 1);
                        valueobj[j][dataname].splice(k, 1);
                        k--;
                    }
                }
            }
            for(let j = 0; j < menuobj.length; j++){
                if(typeof menuobj[j] == "object"){
                    let dataname = Object.keys(menuobj[j])[0];
                    let value = valueobj[j][dataname][0];
                    let nobj = menuobj[j][dataname][0];
                    if(typeof nobj == "object"){
                        let subname = Object.keys(nobj);
                        menuobj[j] = {[dataname]: nobj[subname[0]]};
                        valueobj[j] = {[dataname]: value};
                    }
                    else if(menuobj[j][dataname].length == 1){
                        if(nobj != this.m_defaultlabel){
                            menuobj[j] = [dataname, nobj].join(IDSeparator);
                        }
                        else{
                            menuobj[j] = dataname;
                        }
                        valueobj[j] = value;    
                    }
                }
            }
        }
    }

    ApplytUnitZtitles(id)
    {
        for(let j = 0; j < this.m_currztitles.length; j++){
            let tindex = this.GetSpec("titles", id).indexOf(this.m_currztitles[j]);
            if(tindex >= 0){
                let unit = this.GetSpec("units", id)[tindex];
                if(unit != ""){
                    this.m_currztitles[j] = this.m_currztitles[j]+" ("+unit+")";
                }
            }
        }
    }

    SetScatterConfig(id, axes, frames)
    {
        frames.length = 0;
        for(let j = 0; j < this.GetSpec("scans", id); j++){
            frames.push(j)
        }
        axes.push(this.GetSpec("scans", id));
    }

    PlotCurrentResult(){
        let pp_plot = document.getElementById(this.m_plotdivid);
        pp_plot.innerHTML = "";

        this.SetIndex();
        if(this.m_currid == null){
            return;
        }
        let scatter = this.GetSpec("scatter", this.m_currid);
        let fconf = this.GetFrameConfig();
        if(fconf == null){
            return;
        }

        let comptarget = [];
        let companim = [];
        if(this.m_compenable){
            let comptmp = GetSelections(this.m_complist);
            for(let i = 0; i < comptmp.index.length; i++){
                let aidx = this.m_comp_anims.indexOf(comptmp.value[i]);
                let bidx = this.m_comp_tgts.indexOf(comptmp.value[i]);
                let iidx = comptmp.value[i];
                if(aidx >= 0){
                    companim.push(iidx);
                }
                else if(bidx >= 0){
                    comptarget.push(iidx);
                }
            }
        }
        let mlplotids = [], mlplottexts = [];
        if(this.m_mplotenable){
            mlplotids = GetSelections(this.m_mplotlist).value;
            mlplottexts = GetSelections(this.m_mplotlist).text;
        }

        let axes = [], frames = [];
        let zidxoffset = 0;
        if(fconf.frame == 0 && fconf.plot == 1){
            axes.push(GetSelections(this.m_xaxis).index[0]);
            zidxoffset = 1;
        }
        else if(scatter){
            this.SetScatterConfig(this.m_currid, axes, frames);
        }
        else{
            axes = CopyJSON(this.m_plotdims[fconf.xyidx][0]);
            frames = CopyJSON(this.m_plotdims[fconf.xyidx][1]);    
        }
        this.CreateAnimationPlot(pp_plot, this.m_currid, axes, frames, companim, comptarget, mlplotids, mlplottexts, zidxoffset);
    }

    CreateAnimationPlot(pp_plot, id, axidx, fridx, companim, comptarget, mlplotids, mlplottexts, zidxoffset)
    {
        let axes = Array.from(axidx);
        let frames = Array.from(fridx);
        while(frames.length < 2){
            frames.push(-1);
        }
        if(axes.length == 1){
            axes.push(-1);
        }

        let scatter = this.GetSpec("scatter", id);
        let itemidx, itemtexts;
        if(scatter){
            itemidx = [this.GetSpec("scans", id)];
            itemtexts = {text: ""};
        }
        else{
            itemtexts = GetSelections(this.m_zaxis);
            itemidx = itemtexts.index;
            for(let j = 0; j < itemidx.length; j++){
                itemidx[j] += this.GetSpec("dimension", id)-zidxoffset;
            }    
        }

        let iscomp = (companim.length+comptarget.length) > 0;
        let axindices, itemindices, dataname, citeminices;
        let ncomplots = iscomp ? itemidx.length : Math.min(1, itemidx.length);
        let nplots = ncomplots+mlplotids.length;
        let areas = [document.createElement("div"), document.createElement("div")];
        areas[0].className = "flex-grow-1";
        let stylestr = "display: grid; grid-template-columns: 1fr";
        if(nplots > 1){
            for(let j = 1; j < this.GetPlotCols(); j++){
                stylestr += " 1fr";
            }
        }
        areas[0].style = stylestr;

        pp_plot.appendChild(areas[1]);
        pp_plot.appendChild(areas[0]);
        let plotparents = [];
        for(let n = 0; n < nplots; n++){
            plotparents.push(document.createElement("div"));
            plotparents[n].className = "d-flex flex-grow-1";
            areas[0].appendChild(plotparents[n]);
        }
        this.m_plotwindow = new Array(nplots);

        let titles = this.GetSpec("titles", id);

        for(let np = 0; np < nplots; np++){
            citeminices = [];
            let caxes = [];
            if(np < ncomplots){
                axindices = Array.from(axidx);
                if(this.GetSpec("scatter", id)){
                    for(let i = this.GetSpec("scans", id)+1; i < this.GetSpec("titles", id).length; i++){
                        axindices.push(i);
                    }
                    itemindices = itemidx;
                }
                else if(iscomp){
                    itemindices = [itemidx[np]];
                    axindices.push(itemidx[np]);    
                }
                else{
                    itemindices = itemidx;
                    axindices = axidx.concat(itemidx);
                }
                dataname = this.GetSpec("dataname", id);
                for(let nc = 0; nc < companim.length; nc++){
                    let ctitles = this.GetSpec("titles", companim[nc]);
                    let sctitles = this.GetSpec("titles", companim[nc], true);
                    let mtitles = this.GetSpec("titles", id);
                    let smtitles = this.GetSpec("titles", id);
                    citeminices.push([])
                    for(let ji = 0; ji < itemindices.length; ji++){
                        let cidx = ctitles.indexOf(mtitles[itemindices[ji]]);
                        if(cidx < 0){
                            cidx = sctitles.indexOf(smtitles[itemindices[ji]]);
                        }
                        citeminices[nc].push(cidx);
                    }
                    if(axes[1] < 0){
                        let cax = ctitles.indexOf(mtitles[axes[0]]);
                        if(cax < 0){
                            cax = sctitles.indexOf(smtitles[axes[0]]);
                        }
                        caxes.push([cax, -1]);
                    }
                    else{
                        caxes.push(axes);
                    }
                }
            }
            else{
                id = mlplotids[np-ncomplots];
                frames = []; axes = [];
                if(this.GetSpec("scatter", id)){
                    this.SetScatterConfig(id, axes, frames);
                    axindices = Array.from(axes);
                    for(let i = this.GetSpec("scans", id)+1; i < this.GetSpec("titles", id).length; i++){
                        axindices.push(i);
                    }
                    itemindices = [this.GetSpec("scans", id)];
                }
                else{
                    let isok = true;
                    for(let j = 0; j < fridx.length; j++){
                        let fi = this.GetSpec("titles", id).indexOf(titles[fridx[j]]);
                        if(fi < 0){
                            isok = false;
                            break;
                        }
                        frames.push(fi);
                    }
                    if(!isok){
                        continue;
                    }
    
                    axindices = []; 
                    for(let j = 0; j < this.GetSpec("dimension", id); j++){
                        if(frames.indexOf(j) >= 0){
                            continue;
                        }
                        axindices.push(j);
                        axes.push(j);
                    }
                    if(axes.length <= 0 || axes.length > 2){
                        continue;
                    }
    
                    let pitems = id.split(IDSeparator);
                    if(pitems.length < 3){
                        Alert("Fatal Error in Post-Processor");
                        continue;
                    }
                    let jindex = this.GetSpec("titles", id).indexOf(pitems[2]);
                    if(jindex < 0){
                        continue;
                    }
                    itemindices = [jindex];
                    axindices.push(jindex);
                }
                while(frames.length < 2){
                    frames.push(-1);
                }
                if(axes.length == 1){
                    axes.push(-1);
                }
                companim = [];
            }
            let axtitles = this.GetAxisTitles(id, axindices, axes[1] < 0, companim);
            let si = this.ArrangeSlicedData(id, axes, frames, companim, itemindices, caxes, citeminices);
            let link2d = this.GetSpec("link2d", id);
            let plobj = {};

            plobj.animlegend = [];
            if(si.length == 1){
                if(np < ncomplots){
                    plobj.animlegend = itemtexts.text;
                }
                else{
                    plobj.animlegend = [this.GetSpec("titles", si[0][1])[si[0][2]]]
                }
            }
            else{
                plobj.animlegend = new Array(si.length);
                for(let s = 0; s < si.length; s++){
                    let leglocs = [];
                    if(this.GetSpec("details", id).length >= 2){
                        leglocs.push(this.GetSpec("details", id)[si[s][0]]);
                    }
                    if(iscomp){
                        leglocs.push(this.GetSpec("dataname", si[s][1]));
                    }
                    if(itemindices.length > 1 || nplots > 1){
                        leglocs.push(this.GetSpec("titles", si[s][1])[si[s][2]]);
                    }
                    plobj.animlegend[s] = leglocs.join(": ");
                }

                let isdupl = new Array(si.length);
                isdupl.fill(false);
                for(let s = 0; s < si.length; s++){
                    for(let p = s+1; p < si.length; p++){
                        if(plobj.animlegend[s] == plobj.animlegend[p]){
                            isdupl[s] = true;
                            isdupl[p] = true;
                        }
                    }
                }
                for(let s = 0; s < si.length; s++){
                    if(isdupl[s]){
                        plobj.animlegend[s] = si[s][1];
                    }
                }
            }
        
            if(axes[1] < 0){
                plobj.dimension = 1;
                plobj.compdata = [];
                if(iscomp){
                    let xtl = this.GetSpec("titles", id)[axindices[0]];
                    let ytl = [this.GetSpec("titles", id)[axindices[1]]];
                    let legend, obj;
                    for(let i = 0; i < comptarget.length; i++){
                        let compid = comptarget[i];
                        let dataname = this.GetSpec("dataname", compid);
                        if(this.GetSpec("details", compid).length > 0){
                            for(let j = 0; j < this.GetSpec("details", compid).length; j++){
                                if(this.GetSpec("titles", compid).indexOf(xtl) < 0 && xtl == "Energy"){
                                    xtl = "Harmonic Energy";
                                }
                                obj = {data:this.GetSpec("dataset", compid)[j], titles:this.GetSpec("titles", compid)};
                                legend = [this.GetSpec("details", compid)[j]+": "+dataname];
                                let mdata = GetPlotConfig1D(obj, xtl, ytl, legend);
                                plobj.compdata.push(mdata[0]);
                            }
                        }
                        else{
                            obj = {data:this.GetSpec("dataset", compid), titles:this.GetSpec("titles", compid)};
                            legend = [dataname];
                            let mdata = GetPlotConfig1D(obj, xtl, ytl, legend);
                            plobj.compdata.push(mdata[0]);
                        }
                    }
                }
            }
            else{
                let ztitles = GetSelections(this.m_zaxis);
                this.m_currztitles = CopyJSON(ztitles.value);
                this.ApplytUnitZtitles(id)
                plobj.dimension = 2;
                plobj.ztitle = ztitles.value[0];
                if(axtitles.length != si.length+2){
                    axtitles.length = 2;
                    for(let s = 0; s < si.length; s++){
                        axtitles.push(plobj.animlegend[s]);
                    }    
                }
            }
            plobj.vardata = this.m_vardata;           
            plobj.data = this.m_slicedata;
            plobj.ftitles = this.m_ftitles;
            plobj.fdata = this.m_fdata;
            plobj.axtitles = axtitles;
            plobj.scatter = this.GetSpec("scatter", id);

            let plot_configs = CopyJSON(GUIConf.def_plot_configs);
            if(Settings.plotconfigs.hasOwnProperty(axtitles[plobj.dimension])){
                plot_configs = Settings.plotconfigs[axtitles[plobj.dimension]];
            }
            else{
                Settings.plotconfigs[axtitles[plobj.dimension]] = plot_configs;
            }

            let frameindices = [0, 0];
            let subcols = this.GetSubPlotCols();
            if(plobj.data.length == 1){
                subcols = null;
            }
            for(let j = 0; j < plobj.fdata.length; j++){
                let nmin = 0, vmin = Math.abs(plobj.fdata[j][0]);
                for(let n = 1; n < plobj.fdata[j].length; n++){
                    if(Math.abs(plobj.fdata[j][n]) < vmin){
                        nmin = n;
                        vmin = Math.abs(plobj.fdata[j][n]);
                    }
                }
                frameindices[j] = nmin;
            }
            this.m_plotwindow[np] = new PlotWindow(plotparents[np], 
                this.m_plotid+np.toString(), plobj, plot_configs, dataname, subcols, 
                frameindices, -1, 0, areas[1], np > 0 || frames[0] < 0, null, link2d);
        }

        if(nplots > 0){
            plotparents[0].addEventListener("slidechange", (e)=>{
                for(let n = 1; n < nplots; n++){
                    this.m_plotwindow[n].ShowSlide(false, e.detail.slices);
                }
            });    
        }
    }

    SetFrames(details, dataid, frames){
        this.m_fdata = [];
        this.m_ftitles = [];
        let nframes = [];
        for(let j = 0; j < 2; j++){
            if(frames[j] < 0){
                nframes.push(1);
                this.m_fdata.push([0]);
                this.m_ftitles.push("");
            }
            else{
                if(details.length > 0){
                    nframes.push(this.GetSpec("dataset", dataid)[0][frames[j]].length);
                    this.m_fdata.push(this.GetSpec("dataset", dataid)[0][frames[j]]);
                }
                else{
                    nframes.push(this.GetSpec("dataset", dataid)[frames[j]].length);
                    this.m_fdata.push(this.GetSpec("dataset", dataid)[frames[j]]);
                }
                this.m_ftitles.push(this.GetSpec("titles", dataid)[frames[j]]);
            }
        }
        return nframes;
    }

    ArrangeSlicedData(
        dataid,  // id for the primary data
        axes,  // indices for x (& y) axes to plot
        frames, // indices for the variables to sweep
        compindices, // data indices for the comparative plot
        mitems, // main items to plot (indices, should be an array)
        caxes, // axes of comparative item
        citems // comparative items to plot
    )
    {
        let details = this.GetSpec("details", dataid);
        let nframes = this.SetFrames(details, dataid, frames);
        let link2d = this.GetSpec("link2d", dataid);

        let indices = [dataid, ...compindices];
        let items = [mitems, ...citems];
        if(indices.length != items.length){
            Alert("Invalid combination for comparative plot.");
            return;
        }
        let dnx = Math.max(1, details.length);

        let ntotal = mitems.length*dnx;
        for(let n = 0; n < citems.length; n++){
            if(citems[n] < 0){
                continue;
            }
            let dnxc = Math.max(1, this.GetSpec("details", compindices[n]).length);
            ntotal += citems[n].length*dnxc;
        }

        this.m_vardata = new Array(ntotal);
        let si = new Array(ntotal);
        let nd = new Array(ntotal);
        let mn = 0;
        let scatter;
        for(let m = 0; m < indices.length; m++){
            scatter = this.GetSpec("scatter", indices[m]);
            details = this.GetSpec("details", indices[m]);
            dnx = Math.max(1, details.length);
            for(let d = 0; d < dnx; d++){
                let datasets = details.length > 0 ? this.GetSpec("dataset", indices[m])[d] : this.GetSpec("dataset", indices[m]);
                for(let i = 0; i < items[m].length; i++){
                    if(items[m][i] < 0){
                        continue;
                    }
                    si[mn] = [d, indices[m], items[m][i]];
                    this.m_vardata[mn] = [[0], [0]];
                    if(scatter){
                        this.m_vardata[mn][1] = new Array(2);
                    }
                    else{
                        let tax = m == 0 ? axes : caxes[m-1];
                        for(let j = 0; j < 2; j++){
                            if(tax[j] >= 0){
                                this.m_vardata[mn][j] = datasets[tax[j]];
                            }
                        }
                    }
                    nd[mn] = new Array(4);
                    if(scatter){
                        nd[mn][0] = nd[mn][1] = nd[mn][3] = 1;
                        nd[mn][2] = this.GetSpec("dimension", indices[m])+1;
                        for(let i = 0; i < this.GetSpec("scans", indices[m]); i++){
                            nd[mn][i] = datasets[i].length;
                        }
                    }
                    else{
                        for(let i = 0; i < 4; i++){
                            if(i >= this.GetSpec("dimension", indices[m])){
                                nd[mn][i] = 1;
                            }
                            else{
                                nd[mn][i] = datasets[i].length;
                            }
                        }    
                    }
                    mn++;
                }
            }    
        }

        mn = 0;
        this.m_slicedata = new Array(ntotal);
        for(let m = 0; m < indices.length; m++){
            scatter = this.GetSpec("scatter", indices[m]);
            details = this.GetSpec("details", indices[m]);
            dnx = Math.max(1, details.length);
            for(let d = 0; d < dnx; d++){
                for(let i = 0; i < items[m].length; i++){
                    if(items[m][i] < 0){
                        continue;
                    }
                    this.m_slicedata[mn] = new Array(nframes[1]);
                    for(let f1 = 0; f1 < nframes[1]; f1++){
                        this.m_slicedata[mn][f1] = new Array(nframes[0]);
                        for(let f0 = 0; f0 < nframes[0]; f0++){
                            if(link2d && f1 != f0){
                                continue;
                            }
                            this.m_slicedata[mn][f1][f0] = new Array(this.m_vardata[mn][1].length);
                            for(let m1 = 0; m1 < this.m_vardata[mn][1].length; m1++){
                                this.m_slicedata[mn][f1][f0][m1] = new Array(this.m_vardata[mn][0].length);
                            }    
                        }
                    }
                    mn++;
                }
            }
        }

        let n = [0,0,0,0], nl = [0, 0, 0, 0];
        let f1, f0, m1, m0, datar, ridx;

        let isanm = nframes[0] > 1 || nframes[1] > 1;
        mn = 0;
        for(let m = 0; m < indices.length; m++){
            scatter = this.GetSpec("scatter", indices[m]);
            details = this.GetSpec("details", indices[m]);
            dnx = Math.max(1, details.length);
            for(let d = 0; d < dnx; d++){
                let datasets = details.length > 0 ? this.GetSpec("dataset", indices[m])[d] : this.GetSpec("dataset", indices[m]);
                for(let i = 0; i < items[m].length; i++){
                    if(items[m][i] < 0){
                        continue;
                    }
                    for(n[3] = 0; n[3] < nd[mn][3]; n[3]++){
                        for(n[2] = 0; n[2] < nd[mn][2]; n[2]++){
                            for(n[1] = 0; n[1] < nd[mn][1]; n[1]++){
                                for(n[0] = 0; n[0] < nd[mn][0]; n[0]++){
                                    if(frames[0] < 0){
                                        f0 = 0;
                                    }
                                    else{
                                        f0 = n[frames[0]];
                                    }
                                    if(isanm){ // bug fixed (2024/04/16)
                                        m0 = n[axes[0]]; 
                                    }
                                    else{
                                        m0 = n[0];
                                    }

                                    ridx = GetIndexMDV(nd[mn], n, 4);
                                    if(frames[1] < 0){
                                        f1 = 0;
                                    }
                                    else{
                                        f1 = n[frames[1]];
                                    }
                                    if(axes[1] < 0){
                                        m1 = 0;
                                    }
                                    else{
                                        if(isanm){ // bug fixed (2024/04/16)
                                            m1 = n[axes[1]];
                                        }
                                        else{
                                            m1 = n[1];
                                        }
                                    }
                                    if(link2d){
                                        if(f1 != f0){
                                            continue;
                                        }
                                        for(let j = 0; j < 4; j++){
                                            nl[j] = n[j];
                                        }
                                        nl[frames[1]] = 0;
                                        ridx = GetIndexMDV(nd[mn], nl, 4);
                                    }
                                    if(scatter){
                                        let nfr = n[1]*nd[mn][0]+n[0];
                                        let nxy = n[3]*nd[mn][2]+n[2];
                                        if(frames[0] < 0){
                                            this.m_slicedata[mn][f1][f0][n[2]] = datasets[nxy];
                                        }
                                        else{
                                            this.m_slicedata[mn][f1][f0][n[2]] = datasets[items[m][i]][nfr][nxy];
                                        }
                                    }
                                    else{
                                        datar = datasets[items[m][i]][ridx];
                                        this.m_slicedata[mn][f1][f0][m1][m0] = datar;    
                                    }
                                }
                            }                    
                        }   
                    }
                    mn++;
                }
            }
        }
        return si;
    }

    GetFrameConfig(){
        let plotdim, framedim, xyidx;
        if(this.m_currid < 0){
            return null;
        }
        if(this.GetSpec("scatter", this.m_currid)){
            xyidx = -1;
            plotdim = this.GetSpec("dimension", this.m_currid);
            framedim = this.GetSpec("scans", this.m_currid);
        }
        else if(this.m_xydiv.classList.contains("d-flex")){
            xyidx = GetSelections(this.m_xyaxis).index[0];
            plotdim = this.m_plotdims[xyidx][0].length;
            framedim = this.m_plotdims[xyidx][1].length;   
        }
        else{
            xyidx = -1;
            if(this.m_plotdims.length == 0){
                plotdim = 1;
            }
            else{
                plotdim = this.m_plotdims[0].length;
            }
            framedim = 0;
        }
        return {plot:plotdim, frame:framedim, xyidx:xyidx};
    }

    GetAxisTitles(dataid, axindices, is1d, companim = [])
    {
        let axtitles = [];
        let unitless = is1d && axindices.length > 2;     
        for(let j = 0; j < axindices.length; j++){
            let i = axindices[j];
            if(unitless && j > 1){
                axtitles[1] += ", "+this.GetSpec("titles", dataid)[i];
                continue;
            }
            let unit = "";
            if(this.GetSpec("units", dataid)[i] != "-" && (!unitless || j == 0)){
                unit = ConvertPow2Super(this.GetSpec("units", dataid)[i]);
            }
            if(unit != ""){
                axtitles.push(this.GetSpec("titles", dataid)[i]+" ("+unit+")");
            }
            else{
                axtitles.push(this.GetSpec("titles", dataid)[i]);
            }
        }
        for(let j = 0; j < companim.length; j++){
            axtitles.push(axtitles[axtitles.length-1]);
        }
        return axtitles;
    }

    StartAnimation(){
        if(this.m_plotwindow.length > 0){
            this.m_plotwindow[0].StartAnimation();
        }
    }

    SwitchSlide(slides){
        if(this.m_plotwindow.length > 0){
            if(typeof(slides) == "number"){
                slides = [slides, 0];
            }
            if(Array.isArray(slides)){
                this.m_plotwindow[0].SwitchSlide(slides);
            }
        }
    }
}

// post-post processing
function RunPostProcess()
{
    GUIConf.input[PostPLabel] = GUIConf.GUIpanels[PostPLabel].JSONObj; // to save in the parameter file
    let obj = GUIConf.GUIpanels[PostPLabel].ExportPostPrms();
    if(obj[InputLabel] == null){
        Alert("Input parameters not assigned.")
        return;
    }

    let postconf = GUIConf.GUIpanels[PostPLabel].JSONObj;
    if(postconf[PostProcessPrmLabel.item[0]] == PostPPartDistLabel){
        let exprms = GUIConf.GUIpanels[PostPLabel].GetExprms();
        let steps = exprms[StepCoordLabel].length;
        let slices = exprms[SliceCoordLabel].length;
        if(postconf[PostProcessPrmLabel.timerange[0]] == PostPIntegPartialLabel){
            slices = Math.abs(postconf[PostProcessPrmLabel.timewindow[0]][1]-postconf[PostProcessPrmLabel.timewindow[0]][0])+1;
        }
        if(postconf[PostProcessPrmLabel.zrange[0]] == PostPIntegPartialLabel){
            steps = Math.abs(postconf[PostProcessPrmLabel.zwindow[0]][1]-postconf[PostProcessPrmLabel.zwindow[0]][0])+1;
        }
        let totalslice = steps*slices;
        if(totalslice > 100){
            let msg = "Number of slices x steps ("+ totalslice.toString()+") is large. Really proceed?";
            ShowDialog("Warning", false, false, msg, null, () => {
                DoPostProcess();
            });
            return;
        }    
    }
    DoPostProcess();
}

function DoPostProcess()
{
    let obj = GUIConf.GUIpanels[PostPLabel].ExportPostPrms();
    let postconf = GUIConf.GUIpanels[PostPLabel].JSONObj;
    if(Framework == TauriLabel || Framework.includes("python")){
        let ppid = "postp-process";
        let datapath = obj[DataNameLabel];
        let idx = datapath.lastIndexOf(".json");
        let serial = postconf[PostProcessPrmLabel.serialpp[0]];
        if(serial < 0){
            datapath = datapath.substring(0, idx)+"-pp"+".json";
        }
        else{
            datapath = datapath.substring(0, idx)+"-pp"+postconf[PostProcessPrmLabel.serialpp[0]].toString()+".json";
        }
        GUIConf.simproc.push(new SimulationProcess(true, 
                obj, datapath, GUIConf.simproc.length, ppid, GUIConf.postprocessor, true));
        document.getElementById(ppid).appendChild(Last(GUIConf.simproc).GetList());
        document.getElementById("postp-process-parent").classList.remove("d-none");
        Last(GUIConf.simproc).Start(true);
    }
    else{
        let dataname = GUIConf.postprocessor.GetCurrentDataName();
        ExportObjects(obj, dataname);
    }
    if(postconf[PostProcessPrmLabel.serialpp[0]] >= 0){
        postconf[PostProcessPrmLabel.serialpp[0]]++;
        GUIConf.GUIpanels[PostPLabel].SetPanel();
    }    
}

function PostProcessTab(type)
{
    let ids = ["postp-view", "postp-conf"];
    document.getElementById(ids[type]).classList.remove("d-none");
    document.getElementById(ids[1-type]).classList.add("d-none");
}
