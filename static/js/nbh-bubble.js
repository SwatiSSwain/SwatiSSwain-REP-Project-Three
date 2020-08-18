// @TODO: YOUR CODE HERE!

//Function to resize svg for any screen size
function responsivefy(svg) {
  // container will be the DOM element 
  // that the svg is appended to
  // we then measure the container
  // and find its aspect ratio
  const container = d3.select(svg.node().parentNode),
      width = parseInt(svg.style('width'), 10),
      height = parseInt(svg.style('height'), 10),
      aspect = width / height;
 
  // set viewBox attribute to the initial size
  // control scaling with preserveAspectRatio
  // resize svg on inital page load
  svg.attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMinYMid')
      .call(resize);
 
  // add a listener so the chart will be resized
  // when the window resizes
  // multiple listeners for the same event type
  // requires a namespace, i.e., 'click.foo'
  // api docs: https://goo.gl/F3ZCFr
  d3.select(window).on(
      'resize.' + container.attr('id'), 
      resize
  );
 
  // this is the code that resizes the chart
  // it will be called on load
  // and in response to window resizes
  // gets the width of the container
  // and resizes the svg to fill it
  // while maintaining a consistent aspect ratio
  function resize() {
      const w = parseInt(container.style('width'));
      svg.attr('width', w);
      svg.attr('height', Math.round(w / aspect));
  }
};


// svg params
let svgWidth = 960;
let svgHeight = 500;

let margin = {
  top: 20,
  right: 40,
  bottom: 80,
  left: 100
};

let width = svgWidth - margin.left - margin.right;
let height = svgHeight - margin.top - margin.bottom;

// Create an SVG wrapper, append an SVG group that will hold our chart,
// and shift the latter by left and top margins.
let svg = d3.select("#scatter")  
  .append("svg")
  .attr("width", svgWidth)
  .attr("height", svgHeight)
  .call(responsivefy); // call responsivefy to resize chart

 // Append an SVG group
let chartGroup = svg.append("g")
  .attr("transform", `translate(${margin.left}, ${margin.top})`);

// Initial Params for X and Y axis
let chosenXAxis = "race_use_of_force";
let chosenYAxis = "police_use_of_force_cnt";

// function used for updating x-scale let upon click on axis label
function xScale(data, chosenXAxis) {
  // create scales
  let xLinearScale = d3.scaleLinear()
    .domain([d3.min(data, d => d[chosenXAxis]) * 0.8,
      d3.max(data, d => d[chosenXAxis]) * 1.2
    ])
    .range([0, width]);

  return xLinearScale;

}

// function used for updating y-scale let upon click on axis label
function yScale(data, chosenYAxis) {
  // create scales
  let yLinearScale = d3.scaleLinear()
    .domain([d3.min(data, d => d[chosenYAxis]) * 0.8,
      d3.max(data, d => d[chosenYAxis]) * 1.2
    ])
    .range([height, 0]);

  return yLinearScale;

}

// function used for updating xAxis let upon click on axis label
function renderAxes(newXScale, xAxis) {
  let bottomAxis = d3.axisBottom(newXScale);

  xAxis.transition()
    .duration(1000)
    .call(bottomAxis);

  return xAxis;
}

// function used for updating Y Axis let upon click on axis label
function renderAxesY(newYScale, yAxis) {
  let leftAxis = d3.axisLeft(newYScale);

  yAxis.transition()
    .duration(1000)
    .call(leftAxis);

  return yAxis;
}

// setup fill color
let cValue = function(d) { 
  if (chosenXAxis === "median_income") {
    return d.income_group;
  }
  else if (chosenXAxis === "race_use_of_force") {
    return d.race_use_of_force_type
  }
  else if (chosenXAxis === "race_neighborhood") {
    return d.race_neighborhood_type
  }
},
    color = d3.scaleOrdinal(d3.schemeCategory10);
  



// function used for updating circles group with a transition to
// new circles
function renderCircles(circlesGroup, newXScale, chosenXAxis, newYScale, chosenYAxis) {

  circlesGroup.transition()
    .duration(1000)
    .attr("cx", d => newXScale(d[chosenXAxis]))
    .attr("cy", d => newYScale(d[chosenYAxis]))
    .style("fill", function(d) {
      return color(cValue(d))})

  return circlesGroup;
}

function resetLegend(legend) {
  // legend = svg.selectAll(".legend")
  //     .data(color.domain())
  //     .enter().append("g")
  //     .attr("class", "legend")
  //     .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  legend.exit().remove()
  //legend.exit().remove("g")

  
  callLegend(legend) 

  return legend;
}

function callLegend(legend){
  renderLegend(legend) 

  return legend;
}

function renderLegend(legend) {  

  legend = svg
         .selectAll(".legend")
         .data(color.domain())
         .enter()
         .append("g")
         .attr("class", "legend")
         .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  // draw legend colored rectangles
  legend.append("rect")
      .attr("x", width - 18)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill", color);

  // draw legend text
  legend.append("text")
      .attr("x", width - 24)
      .attr("y", 9)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(function(d) { 
        console.log(d)
        return d })
    return legend;
}

// function used for updating circle labels with a transition
function renderText(textGroup, newXScale, chosenXAxis, newYScale, chosenYAxis) {

  textGroup.transition()
    .duration(1000)
    .attr("x", d => newXScale(d[chosenXAxis]))
    .attr("y", d => newYScale(d[chosenYAxis]));

  return textGroup;
}

// function used for updating circles group with new tooltip
function updateToolTip(chosenXAxis,chosenYAxis, circlesGroup) {
  
  //select x label
    let label="";
    
    if (chosenXAxis === "race_use_of_force") {
      label = "Subject Race: ";
    }
    else if (chosenXAxis === "race_neighborhood") {
        label = "Neighborhood Demographics: "
    }
    else if (chosenXAxis === "median_income"){
      label = "Household Income: ";
    }
    
  //select y label
    let yLabel="";  
    
    if (chosenYAxis === "police_use_of_force_cnt") {
      yLabel = "Use of Force Cases: ";
    }
    else if (chosenYAxis === "cases_count") {
        yLabel = "Police Incidents: "
    }
    
  
    let toolTip = d3.tip()
      .attr("class", "d3-tip")
      .offset([80, -60])
      .html(function(d) {
        if (chosenXAxis === "median_income") {
          return (`${d.neighborhood_name}<br>${label} $${d.median_income_text}<br>Income Group: ${d.income_group}<br>${yLabel} ${d[chosenYAxis]}`)
        }
        if (chosenXAxis === "race_use_of_force") {
          return (`${d.neighborhood_name}<br>${label} ${d.race_use_of_force_type} (${d[chosenXAxis]}%)<br>${yLabel} ${d[chosenYAxis]}`)
        }
        else {
          return (`${d.neighborhood_name}<br>${label} ${d.race_neighborhood_type} (${d[chosenXAxis]}%)<br>${yLabel} ${d[chosenYAxis]}`)
        }
      });
  
    circlesGroup.call(toolTip);
  
    circlesGroup.on("mouseover", function(data) {
      toolTip.show(data);
    })
  
    // onmouseout event
    .on("mouseout", function(data, index) {
    toolTip.hide(data);
    });
  
    return circlesGroup;
  }

// Retrieve data from the json api and execute everything below
d3.json('/api/nbh_bubble').then(function(data, err) {
  if (err) throw err;

  // parse data and convert strint to int

  data.forEach(function(stateData) {
    stateData.race_use_of_force = +stateData.race_use_of_force;
    stateData.police_use_of_force_cnt = +stateData.police_use_of_force_cnt;
    stateData.race_use_of_force = +stateData.race_use_of_force;
    stateData.race_neighborhood = +stateData.race_neighborhood;
    stateData.median_income = +stateData.median_income;
  });

  // xLinearScale function above json import
  let xLinearScale = xScale(data, chosenXAxis);
  
  // Create y scale function
  let yLinearScale = yScale(data, chosenYAxis);
 
  // Create initial axis functions
  let bottomAxis = d3.axisBottom(xLinearScale);
  let leftAxis = d3.axisLeft(yLinearScale);

  // append x axis
  let xAxis = chartGroup.append("g")
    .classed("x-axis", true)
    .attr("transform", `translate(0, ${height})`)
    .call(bottomAxis);

  // append y axis
  let yAxis = chartGroup.append("g")
    .classed("y-axis", true)
    .call(leftAxis);

  // append initial circles
  let circlesGroup = chartGroup.selectAll("circle")
    .data(data)
    .enter()
    .append("circle")
    .classed("stateCircle",true)
    .attr("cx", d => xLinearScale(d[chosenXAxis]))
    .attr("cy", d => yLinearScale(d[chosenYAxis]))
    .attr("r", 17)
    .attr("opacity", ".8")
    .style("fill", function(d) { return color(cValue(d));}) ;

   // append counts
   let textGroup = chartGroup.selectAll(".stateText")
   .data(data)
   .enter()
   .append("text")
   .classed("stateText", true)
   .attr("x", d => xLinearScale(d[chosenXAxis]))
   .attr("y", d => yLinearScale(d[chosenYAxis]))
   .attr("dy", 3)
   .attr("font-size", "10px")
   .text(function(d) {return d.neighborhood_id});

  // draw legend
  let legend = svg.selectAll(".legend")
      .data(color.domain())
      .enter()
      .append("g")
      .attr("class", "legend")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  
  // draw legend colored rectangles
  legend.append("rect")
      .attr("x", width - 18)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill", color);

  // draw legend text
  legend.append("text")
      .attr("x", width - 24)
      .attr("y", 9)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(function(d) { return d })

  

  // Create group for 3 x-axis labels
  let labelsGroup = chartGroup.append("g")
    .attr("transform", `translate(${width / 2}, ${height + 20})`);

  let subjectRaceLabel = labelsGroup.append("text")
    .classed("aText", true)
    .attr("x", 0)
    .attr("y", 20)
    .attr("value", "race_use_of_force") // value to grab for event listener
    .classed("active", true)
    .text("Subject Race (%)");

  let demoLabel = labelsGroup.append("text")
    .classed("aText", true)
    .attr("x", 0)
    .attr("y", 40)
    .attr("value", "race_neighborhood") // value to grab for event listener
    .classed("inactive", true)
    .text("Neighborhood Demographics (%)");

   let incomeLabel = labelsGroup.append("text")
   .classed("aText", true)
    .attr("x", 0)
    .attr("y", 60)
    .attr("value", "median_income") // value to grab for event listener
    .classed("inactive", true)
    .text("Household Income Median");
   
  //create group for 3 y-axis labels
  let yLabelsGroup = chartGroup.append("g")
  .attr("transform", `translate(${0 - margin.left/4}, ${(height/2)})`);

  // append y axis
  let forceLabel = yLabelsGroup.append("text")
        .classed("aText", true)
        .classed("active", true)
        .attr("x", 0)
        .attr("y", 0 - 60)
        .attr("dy", "1em")
        .attr("transform", "rotate(-90)")
        .attr("value", "police_use_of_force_cnt")
        .text("Use of Force Cases");

  let incidentLabel = yLabelsGroup.append("text")
        .classed("aText", true)
        .classed("inactive", true)
        .attr("x", 0)
        .attr("y", 0 - 80)
        .attr("dy", "1em")
        .attr("transform", "rotate(-90)")
        .attr("value", "cases_count")
        .text("Police Incidents");

  
  // updateToolTip function above json api
   circlesGroup = updateToolTip(chosenXAxis, chosenYAxis, circlesGroup);

 // x axis labels event listener
  labelsGroup.selectAll("text")
    .on("click", function() {
      // get value of selection
      let value = d3.select(this).attr("value");
      if (value !== chosenXAxis) {

      //  replaces chosenXAxis with value
        chosenXAxis = value;

      //  functions here found above csv import
      //  updates x scale for new data
        xLinearScale = xScale(data, chosenXAxis);

        // updates x axis with transition
        xAxis = renderAxes(xLinearScale, xAxis);

        //updates circles with new x values
        circlesGroup = renderCircles(circlesGroup, xLinearScale, chosenXAxis, yLinearScale, chosenYAxis);
        
        // Update state abbr
        textGroup = renderText(textGroup, xLinearScale, chosenXAxis, yLinearScale, chosenYAxis);

        // updates tooltips with new info
        circlesGroup = updateToolTip(chosenXAxis, chosenYAxis, circlesGroup);

        //update legend
        legend = resetLegend(legend);

        // changes classes to change bold text
        if (chosenXAxis === "race_use_of_force") {
          subjectRaceLabel
            .classed("active", true)
            .classed("inactive", false);
          demoLabel
            .classed("active", false)
            .classed("inactive", true);
          incomeLabel
            .classed("active", false)
            .classed("inactive", true);
        }
        else if (chosenXAxis === "race_neighborhood") {
          demoLabel
            .classed("active", true)
            .classed("inactive", false);
          subjectRaceLabel
            .classed("active", false)
            .classed("inactive", true);
          incomeLabel
            .classed("active", false)
            .classed("inactive", true);
        }
        else if (chosenXAxis === "median_income"){
        incomeLabel  
          .classed("active", true)
          .classed("inactive", false);
        subjectRaceLabel
          .classed("active", false)
          .classed("inactive", true);
        demoLabel
          .classed("active", false)
          .classed("inactive", true);
        }
      }
  });


  // y axis labels event listener
  yLabelsGroup.selectAll("text")
    .on("click", function() {
      // get value of selection
      let value = d3.select(this).attr("value");
      if (value !== chosenYAxis) {

        //  replaces chosenYAxis with value
        chosenYAxis = value;

        //  functions here found above csv import
        //  updates y scale for new data
        yLinearScale = yScale(data, chosenYAxis);

        // updates y axis with transition
        yAxis = renderAxesY(yLinearScale, yAxis);

        //updates circles with new y values
        circlesGroup = renderCircles(circlesGroup, xLinearScale, chosenXAxis, yLinearScale, chosenYAxis);
        
        // Update state abbr
        textGroup = renderText(textGroup, xLinearScale, chosenXAxis, yLinearScale, chosenYAxis);

        // updates tooltips with new info
        circlesGroup = updateToolTip(chosenXAxis, chosenYAxis, circlesGroup);

        //update legend
        legend = resetLegend(legend);


        // changes classes to change bold text
        if (chosenYAxis === "police_use_of_force_cnt") {
          forceLabel
            .classed("active", true)
            .classed("inactive", false);
          incidentLabel
            .classed("active", false)
            .classed("inactive", true);
        }
        
        else if (chosenYAxis === "cases_count"){
        incidentLabel  
          .classed("active", true)
          .classed("inactive", false);
        forceLabel
          .classed("active", false)
          .classed("inactive", true);
        }
      }
  });

  
  }).catch(function(error) {
    console.log(error);
});

