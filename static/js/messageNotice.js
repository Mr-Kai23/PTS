$(function () {

    //检测待办事项
    function checkTodo() {
        $.ajax({
            type: 'GET',
            url: "/process/order/message",
            // data: { csrfmiddlewaretoken: '{{ csrf_token }}' },
            success: function (data) {

                //如果用户没有该地址相应的权限，那么data返回的是一个html
                if(typeof(data) != 'string'){
                    showTodo(data['count']);
                }

            },
            error: function (e) {

            }
        })
    }

    //显示有几条待办事项
    function showTodo(count) {
        console.log(count);
        if (count) {
            $("span[id='message']").css({
                "font-color": "white",
                'display': 'inline-block',
                'min-width': '10px',
                'padding': '3px 7px',
                'text-align': 'center',
                'white-space': 'nowrap',
                'vertical-align': 'baseline',
                'background-color': '#ff2235',
                'border-radius': '10px',
                'font-size': '12px',
                'font-weight': 'bold',
                'line-height': '1',
                'margin-left': '10px',
            });
            //假如两个参数都有值，那么将值赋予到标签中


            if (count != 0) {
                $('span#message').text(count);
            } else {
                $('span#message').remove();
            }

        }

    }

    setTimeout(function () {
        checkTodo();
    }, 1000);

    setInterval(function () {
        checkTodo();
    }, 60000);

})