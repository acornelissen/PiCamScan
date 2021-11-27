/*	Yes, yes I know, global variables are bad.
	Set the initial frame total and first frame on load
*/
var frame_total = document.getElementById('frames').value;
var frame_nr = 1;

// Update frame total and error display when value changes
document.getElementById('frames').onblur = function() {
	frame_total = document.getElementById('frames').value;
	frame_nr = 1;
	if (!document.getElementById('frame_error').classList.contains("is-hidden")) {
		document.getElementById('frame_error').classList.add("is-hidden");
	}
}


// And scan! After successful capture, decrement and increment values as needed, and redirect to DNG download
document.getElementById('goscan').onclick = function() {

	if (document.getElementById('frames').value > 0) {
		document.getElementById('goscan').textContent = "Capturing...";
		document.getElementById('goscan').disabled = true;

		fetch('/capture?filename='+document.getElementById('filepre').value+'-'+frame_nr)
		.then(
			async function(response) {
				const text = await response.text();
	
				document.getElementById('goscan').textContent = "Scan";
				document.getElementById('goscan').disabled = false;
				document.getElementById('frames').value = frame_total - 1;

				frame_nr++;

				window.location = '/output/'+text+'.dng';
			}
		)
		.catch(function(err) {
			console.log('Fetch Error :-S', err);
		});
	}
	else if (frame_total == 0) {
		console.log('At last frame');
		if (document.getElementById('frame_error').classList.contains("is-hidden")) {
			document.getElementById('frame_error').classList.remove("is-hidden");
		}
	}

	return false;
}