var allResults;
d3.json("all_results.json", function(results){
  allResults = results;
  drawYear("2017");
});


function drawYear(year){
  d3.select("#diagram-div").node().innerHTML = "";
  d3.select("#event-select").node().value = "Any";

  var subResults = allResults.filter(function(d){ return d.year == year });
  subResults.map(function(d){ drawResults(d)});
}

function drawEvent(event_name){
  d3.select("#diagram-div").node().innerHTML = "";
  d3.select("#year-select").node().value = "Any";

  event_name = "The " + event_name;
  var subResults = allResults.filter(function(d){ return d.event_name == event_name });
  subResults.map(function(d){ drawResults(d)});
}


function getCountryFlagName(teamName){
  var countries = ["Ireland", "Holland", "Germany", "USA", "Portugal", "Greece", "China", "Switzerland", "Australia", "New Zealand", "Argentina", "Norway", "Estonia", "Bulgaria", "Russia", "Poland", "South Africa", "Japan", "Belarus", "Slovenia", "Canada", "Czech Republic", "Azerbaijan", "Belgium", "Italy", "Spain", "Denmark", "France", "Ukraine", "Sweden"];

  for (var i=0; i<countries.length; i++){
    // If multiple maches, should inidcate
    if (teamName.indexOf(countries[i]) != -1){
      return countries[i];
    }
  }


var codes = [
{code: "GER", name: "Germany"},
{code: "CHN", name: "China"},
{code: "NED", name: "Holland"},
{code: "AUS", name: "Australia"},
{code: "NZL", name: "New Zealand"},
{code: "CAN", name: "Canada"},
{code: "JPN", name: "Japan"},
{code: "U.S.A.", name: "USA"},

{code: "NOR", name: "Norway"},
{code: "FRA", name: "France"},
{code: "IRL", name: "Ireland"}

];

for (var i=0; i<codes.length; i++){
    // If multiple maches, should inidcate
    if (teamName.indexOf(codes[i].code) != -1){
      return codes[i].name;
    }
  }






}

function slugify(name) {
    return name.replaceAll(" ", "-").replaceAll("'", "").toLowerCase();
}


function drawResults(eventDetails){

  var results = eventDetails.results;

  d3.select("#diagram-div")
  .append("h2")
  .text(eventDetails.event_name + " (" + eventDetails.year + ") ")
  .style("margin-bottom", "0px")

  d3.select("#diagram-div")
  .append("p")
  .style("margin-top", "0px")
  .append("small")
  .append("a")
  .attr("href", `https://www.hrr.co.uk/results/?race-year=${eventDetails.year}&result-page=1&trophy=${slugify(eventDetails.event_name)}`)
  .text("Official results")
  

  var svg = d3.select("#diagram-div").append("svg").attr("width", 700).attr("height", 20 + 20 + results.crews.length*30);

  var  margin = {top: 20, right: 20, bottom: 30, left: 50, label: 300, margin_label: 100},
      width = +svg.attr("width") - margin.left - margin.right - margin.label - margin.margin_label,
      height = +svg.attr("height") - margin.top - margin.bottom,
      g = svg.append("g").attr("transform", "translate(" + (margin.left + margin.label) + "," + margin.top + ")");

  var tick_radius = 5, circle_radius = 4;

  var label_g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  var margin_label_g = svg.append("g").attr("transform", "translate(" + (10 + +svg.attr("width") - margin.right - margin.margin_label) + "," + margin.top + ")");

  var flag_g = svg.append("g").attr("transform", "translate(" + (margin.left -30) + "," + margin.top + ")");


  var numCrews = results.crews.length;
  var maxMargin = results.crews[numCrews-1].margin;

  var xScale = d3.scale.linear().domain([0, maxMargin]).range([width, 0]);
  var yScale = d3.scale.linear().domain([0, numCrews]).range([0, height]);

  g.selectAll(".crew-line")
    .data(results.crews)
    .enter()
    .append("line")
    .attr("x1", function(d){

      var crewsMaxMargin = 0;
      for (var i=0; i<results.races.length; i++){
          if (results.races[i].winner == d.crew){
            crewsMaxMargin = Math.max(crewsMaxMargin, results.races[i].margin);
          }
      }
      return xScale(crewsMaxMargin + d.margin);
    })
    .attr("x2", function(d){ return xScale(d.margin); })
    .attr("y1", function(d){ return yScale(d.id) })
    .attr("y2", function(d){ return yScale(d.id) })
    .attr("class", "crew-line");


var labels = label_g.selectAll("text")
          .data(results.crews)
          .enter()
          .append("text")
          .text(function(d){ return d.crew; })
          .attr("y", function(d){ return yScale(d.id) })
          .attr("class", "crew-labels")
          .attr("dy", 0)
          .call(wrap, margin.label);



margin_label_g.append("text")
          .attr("y", - 12)
          .attr("class", "margin-header")
          .attr("dy", 0)
          .text("Losing margin");

var margin_labels = margin_label_g.selectAll(".margin_labels")
          .data(results.crews)
          .enter()
          .append("text")
          .text(function(d){ 
                var race = results.races.filter(function(r){ return r.loser == d.crew })[0]; 
                return race ? race.margin_string : "";
            })
          .attr("y", function(d){ return yScale(d.id) })
          .attr("class", "crew-labels")
          .attr("dy", 0)
          .call(wrap, margin.margin_label)
          .on("mouseover", function(d){ 
            var race = results.races.filter(function(r){ return r.loser == d.crew })[0];
            highlightRace(race);
          })
          .on("mouseout", clearHighLights);



flag_g.selectAll("image")
          .data(results.crews)
          .enter()
          .append("image")
          .attr("y", function(d){ return yScale(d.id) - 12 })// since  text-size is 12px
          .attr("x", 0) 
          .attr("width", 20)
          .attr("height", 20)
          .attr("xlink:href", function(d){ return "flags/" + getCountryFlagName(d.crew) + ".svg"});


var losing_lines = 
  g.selectAll(".lose_line")
    .data(results.races)
    .enter()
    .append("line")
    .attr("x1", function(d){
      var loser = results.crews.filter(function(c){ return c.crew == d.loser })[0]; 
      return xScale(loser.margin);
    })
    .attr("x2", function(d){ 
            var winner = results.crews.filter(function(c){ return c.crew == d.winner })[0];
      return xScale(winner.margin); 
    })
    .attr("y1", function(d){ 
      var loser = results.crews.filter(function(c){ return c.crew == d.loser })[0]; 
      return yScale(loser.id) ;
    })
    .attr("y2", function(d){ 
      var loser = results.crews.filter(function(c){ return c.crew == d.loser })[0]; 
      return yScale(loser.id); 
    })
    .attr("class", "lose-line")
    .on("mouseover", function(d){ highlightRace(d) })
    .on("mouseout", clearHighLights);


losing_lines.style("stroke-dasharray", function(d){ 
  var wonEasily = (d.margin_string.toLowerCase().indexOf("easily")  != -1);
  return wonEasily ? "2,2" : "";
})



var winning_circles = 
g.selectAll(".win-tick")
    .data(results.races)
    .enter()
    .append("line")
    .attr("x1", function(d){ 
      var winner = results.crews.filter(function(c){ return c.crew == d.winner })[0];
      return xScale(winner.margin + d.margin);
       })
    .attr("x2", function(d){ 
      var winner = results.crews.filter(function(c){ return c.crew == d.winner })[0];
      return xScale(winner.margin + d.margin);
       })
    .attr("y1", function(d){ 
      var winner = results.crews.filter(function(c){ return c.crew == d.winner })[0];
      return yScale(winner.id) + tick_radius;
       })
    .attr("y2", function(d){ 
      var winner = results.crews.filter(function(c){ return c.crew == d.winner })[0];
      return yScale(winner.id) - tick_radius;
       })
    .attr("class", "win-tick")
    .on("mouseover", function(d){ highlightRace(d) })
    .on("mouseout", clearHighLights);

winning_circles.append("title").text(function(d){ return d.winner + " beat " + d.loser + " by "+ d.margin_string})



var losing_circles = 
g.selectAll(".lose-circle")
    .data(results.races)
    .enter()
    .append("circle")
    .attr("cx", function(d){ 
      var winner = results.crews.filter(function(c){ return c.crew == d.winner })[0];
      return xScale(winner.margin + d.margin);
       })
    .attr("cy", function(d){ 
      var loser = results.crews.filter(function(c){ return c.crew == d.loser })[0];
      return yScale(loser.id);
       })
    .attr("r", circle_radius)
    .attr("class", "lose-circle")
    .on("mouseover", function(d){ highlightRace(d) })
    .on("mouseout", clearHighLights);


  var difference_line1 = g.append("line").attr("class", "difference-line");
  var difference_line2 = g.append("line").attr("class", "difference-line");


    function clearHighLights(){
        highlightRace({});
        difference_line1.style("visibility", "hidden");
        difference_line2.style("visibility", "hidden");
    }
    function highlightRace(race_data){

        var yellow = "#ffc200";
        winning_circles.style("stroke", function(d){ return d==race_data ? yellow : "black" });
        losing_circles.style("stroke", function(d){ return d==race_data ? yellow : "black" });
        losing_lines.style("stroke", function(d){ return d==race_data ? yellow : "black" });

        margin_labels.style("font-weight", function(d){ return d.crew==race_data.loser ? "bold" : "normal"});
        labels.attr("font-weight", function(d){ return (d.crew == race_data.winner || d.crew  == race_data.loser) ? "bold" : "normal" });

        if (race_data.winner){
          var winner = results.crews.filter(function(c){ return c.crew == race_data.winner })[0];
          var loser = results.crews.filter(function(c){ return c.crew == race_data.loser })[0]; 

          difference_line1
              .attr("x1", xScale(winner.margin + race_data.margin) )
              .attr("x2", xScale(winner.margin + race_data.margin) )
              .attr("y1", yScale(loser.id))
              .attr("y2", yScale(winner.id))
              .style("visibility", null);

          difference_line2
              .attr("x1", xScale(winner.margin) )
              .attr("x2", xScale(winner.margin) )
              .attr("y1", yScale(loser.id))
              .attr("y2", yScale(winner.id))
              .style("visibility", null);
        }
            
    }

losing_circles.append("title").text(function(d){ return d.winner + " beat " + d.loser + " by "+ d.margin_string})

}


// See this block: https://bl.ocks.org/mbostock/7555321
function wrap(text, width) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        y = text.attr("y"),
        dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
      }
    }
  });
}

