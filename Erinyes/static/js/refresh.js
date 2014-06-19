/**
 * Created by jonathans on 6/19/2014.
 */

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