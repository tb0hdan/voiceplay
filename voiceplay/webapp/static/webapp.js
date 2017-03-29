var tgt;

function title_poll() {
    setTimeout(function() {
        $.ajax({
            url: "/api/v1/tracks/current",
            type: "GET",
            success: function(data) {
                $('p.current_track').text('Now playing: ' + data.message);
            },
            dataType: "json",
            complete: title_poll,
            timeout: 5000
        })
    }, 5000);
}

function filter_controls(cls) {
    return cls.includes('button-')
}

function webapp_register() {
    $('body').on('click', 'button.controls', function(evt) {
        evt.preventDefault();
        classes = evt.target.className.split(' ');
        console.log(classes);
        button_cls = classes.filter(filter_controls)[0];
        switch (button_cls) {
            case 'button-play':
                $.post('/api/v1/control/resume');
                break;
            case 'button-pause':
                $.post('/api/v1/control/pause');
                break;
            case 'button-next':
                $.post('/api/v1/control/next');
                break;
            default:
                console.log('Unknown button_cls: ' + button_cls);
        };
    });
    title_poll();
    console.log('done');
}
