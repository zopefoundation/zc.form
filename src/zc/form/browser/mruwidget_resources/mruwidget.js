function zc_mruwidget_toggleQueriesDisplay(id) {
    var element = document.getElementById(id);
    var input = document.getElementById(id+'.visible');

    if (element.style.display == 'none') {
        element.style.display = '';
        input.value = 'yes';
    }
    else {
        element.style.display = 'none';
        input.value = 'no';
    }
}
