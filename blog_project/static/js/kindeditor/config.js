/**
 * Created by Administrator on 2016/6/7.
 */
KindEditor.ready(function(K) {
    window.editor = K.create('textarea',{
        width:'800px',
        height:'200px',
        uploadJson:'/admin/upload/kindeditor'
    });
});