function webapp_register() {
    console.log( "ready!" );
    $('body').on('click', 'button.button-next', function() {
        $.post('/api/v1/control/next');
    });
}