/*������ǰҳ����*/

// var obj=null;
// var As=document.getElementById('topnav').getElementsByTagName('a');
//
// obj = As[0];
// for(i=1;i<As.length;i++){if(window.location.href.indexOf(As[i].href)>=0)
// obj=As[i];}

$('#topnav a').click(function () {
    var f = this;
    $('#topnav a').each(function () { this.id = this == f ? 'topnav_current' : ''
    });
});





