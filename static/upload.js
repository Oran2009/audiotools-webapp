$(document).ready(function() {
    var videoFileName='';
    $('#videoInput').change(function(e){
        videoFileName = e.target.files[0].name;
    });

    $('#videoForm').on('submit', function(event) {

        event.preventDefault();

        var formData = new FormData($('#videoForm')[0]);

        $.ajax({
            xhr : function() {
                var xhr = new window.XMLHttpRequest();

                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        if (videoFileName == '') {
                            alert('No file selected!');
                            $('#videoProgressBar').attr('aria-valuenow', '0').css('width', '0%').text('0%');
                            $('#selectedVideo').text('Selected video file: ');
                            $('#audioProgressBar').attr('aria-valuenow', '0').css('width', '0%').text('0%');
                            $('#selectedAudio').text('Selected audio file: ');
                        }
                        else {
                            console.log('Bytes Loaded: ' + e.loaded);
                            console.log('Total Size: ' + e.total);
                            console.log('Percentage Uploaded: ' + (e.loaded / e.total));

                            var percent = Math.round((e.loaded / e.total) * 100);

                            $('#videoProgressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
                            $('#selectedVideo').text('Selected video file: ' + videoFileName);
                        }

                    }
                });

                return xhr;
            },
            type : 'POST',
            url : '/video_upload',
            data : formData,
            processData : false,
            contentType: false
        });

    });

    var audioFileName='';
    $('#audioInput').change(function(e){
        audioFileName = e.target.files[0].name;
    });

    $('#audioForm').on('submit', function(event) {

        event.preventDefault();

        var formData = new FormData($('#audioForm')[0]);

        $.ajax({
            xhr : function() {
                var xhr = new window.XMLHttpRequest();

                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        if (audioFileName == '') {
                            alert('No file selected!');
                            $('#videoProgressBar').attr('aria-valuenow', '0').css('width', '0%').text('0%');
                            $('#selectedVideo').text('Selected video file: ');
                            $('#audioProgressBar').attr('aria-valuenow', '0').css('width', '0%').text('0%');
                            $('#selectedAudio').text('Selected audio file: ');
                        }
                        else {
                            console.log('Bytes Loaded: ' + e.loaded);
                            console.log('Total Size: ' + e.total);
                            console.log('Percentage Uploaded: ' + (e.loaded / e.total));

                            var percent = Math.round((e.loaded / e.total) * 100);

                            $('#audioProgressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
                            $('#selectedAudio').text('Selected audio file: ' + audioFileName);
                        }

                    }
                });

                return xhr;
            },
            type : 'POST',
            url : '/audio_upload',
            data : formData,
            processData : false,
            contentType: false
        });

    });

});
