document.addEventListener('DOMContentLoaded', function() {
    const tooltip = document.getElementById('tooltip-textbox');
    const svgContainer = document.getElementById('svg-container');
    const svgDoc = svgContainer ? svgContainer.querySelector('svg') : null;
  
    if (svgDoc) {
        const circles = svgDoc.querySelectorAll('circle');
  
        circles.forEach(function(circle) {
            circle.addEventListener('mouseover', function(event) {
                const name = circle.getAttribute('data-name') || 'Data need to show here';
                tooltip.innerHTML = name;
                tooltip.style.display = 'block';
            });
  
            circle.addEventListener('mousemove', function(event) {
                tooltip.style.left = event.pageX + 'px';
                tooltip.style.top = event.pageY + 'px';
            });
  
            circle.addEventListener('mouseout', function() {
                tooltip.style.display = 'none';
            });
        });
    } else {
        console.error("SVG document not found!");
    }
    
    //aaron
    const fromBox = document.getElementById('fromBox');
    const toBox = document.getElementById('toBox');
    fromBox.addEventListener('input', function() {
        performSearch(fromBox.value, 'from');
    });

    toBox.addEventListener('input', function() {
        performSearch(toBox.value, 'to');
    });

    const submitButton = document.getElementById('submitButton');
    if (submitButton) {
        submitButton.addEventListener('click', function(event) {
            event.preventDefault();
  
            const fromBox = document.getElementById('fromBox').value.trim().toLowerCase();
            const toBox = document.getElementById('toBox').value.trim().toLowerCase();
            const algorithm = document.getElementById('select_box').value.trim().toLowerCase();
  
            if (fromBox && toBox && algorithm) {
                fetch(`/api/${algorithm}/?start=${fromBox}&end=${toBox}`)
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(data => { throw new Error(data.error); });
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.route !== 'null') {
                            //markPath(data.route);
                            alert('Route found: ' + data.route.join(' -> ') + '. Total duration: ' + data.duration + ' minutes.');
                        } else {
                            alert('No route found.');
                        }
                    })
                    .catch(error => {
                        alert('Error: ' + error.message);
                        console.error('Error:', error);
                    });
            } else {
                alert('Please enter both "From" and "To" locations.');
            }
        });
    } else {
        console.error("Submit button not found!");
    }
    //aaron
    function performSearch(query, type) {
        if (query.length === 0) {
            return;
        }

        fetch(`/api/search/?query=${query}`)
            .then(response => response.json())
            .then(data => {
                if (type === 'from') {
                    fromBox.setAttribute('list', 'from-datalist');
                    updateDatalist('from-datalist', data.results);
                } else {
                    toBox.setAttribute('list', 'to-datalist');
                    updateDatalist('to-datalist', data.results);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
    //aaron
    function updateDatalist(id, options) {
        let datalist = document.getElementById(id);
        if (!datalist) {
            datalist = document.createElement('datalist');
            datalist.id = id;
            document.body.appendChild(datalist);
        }
        datalist.innerHTML = '';
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            datalist.appendChild(optionElement);
        });
    }
  
    function markPath(route) {
        circles.forEach(circle => {
            const stationName = circle.getAttribute('data-name');
            if (stationName && route.includes(stationName)) {
                circle.setAttribute('fill', 'green'); // Example of highlighting the path by changing fill color
            } else {
                circle.style.opacity = '';
                circle.style.fill = ''; // Resetting fill color and opacity
            }
        });
    }
  });
  