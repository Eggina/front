(function() {
    $(document).ready(() => {
        console.log('custom script running...')

        var check_todas = (e) => {
            var checkbox = e.target;
            for (cb of $('input.form-check-input')) {
                cb.checked = checkbox.checked;
            }
        };

        var uncheck_lead = (e) => {
            $('input#checkbox-todas').get(0).checked = false;
        };

        $('input.form-check-input').not('input#checkbox-todas').change(uncheck_lead);
        $('input#checkbox-todas').change(check_todas);


        $('#sidebarCollapse').click(function() {
            $('#sidebar').toggleClass('active');
        });

        $(function() {
            $('[data-toggle="tooltip"]').tooltip()
            $('[data-toggle="popover"]').popover()
        });

        $('#conf').click(function(e) {
            e.preventDefault();
        });

        $('.popover-dismiss').popover({
            trigger: 'focus'
        });


    });
})();