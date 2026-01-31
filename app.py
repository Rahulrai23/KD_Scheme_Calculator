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
            fetch("/gps-detect", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude
                })
            }).finally(() => {
                window.location.href = "/scheme";
            });
        },
        function() {
            window.location.href = "/scheme";
        },
        { timeout: 8000 }
    );
} else {
    window.location.href = "/scheme";
}
</script>

</body>
</html>
