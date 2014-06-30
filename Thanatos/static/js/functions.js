/***************************************************************************************************
 *
 * Copyright (c) by Jonathan Slattery
 *
 **************************************************************************************************/

function refresh() {
    $.ajax({
        url: '{% url Erinyes %}',
        success: function (data) {
            $('#test').html(data);
        }
    });
    $(function() {
        refresh();
        var int = setInterval("refresh()", 10000);
    });
}

function run_test() {

}