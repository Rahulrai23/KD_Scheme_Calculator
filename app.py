<!DOCTYPE html>
<html>
<head>
  <title>Detecting Location</title>
</head>
<body>

<h3>Detecting your location…</h3>

<script>
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        function(pos) {
            fetch("/scheme", {
                headers: {
                    "X-GPS-State": ""
                }
            });

            fetch("/gps-reverse", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude
                })
            })
            .then(res => res.text())
            .then(state => {
                window.location.href = "/scheme";
            });
        },
        function() {
            window.location.href = "/scheme";
        },
        { enableHighAccuracy: true, maximumAge: 0 }
    );
} else {
    window.location.href = "/scheme";
}
</script>

</body>
</html>
