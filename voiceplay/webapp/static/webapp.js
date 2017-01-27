var tgt;

function webapp_register() {
    function filter_controls(cls) {
        return cls.includes('button-')
    }
    $('body').on('click', 'button.controls', function(evt) {
        classes = evt.target.parentElement.className.split(' ');
        button_cls = classes.filter(filter_controls)[0];
        switch (button_cls) {
            case 'button-play':
                // redir?
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
}