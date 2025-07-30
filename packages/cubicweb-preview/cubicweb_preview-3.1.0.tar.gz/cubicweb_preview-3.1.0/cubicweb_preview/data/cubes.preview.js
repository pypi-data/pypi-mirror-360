function handleInlinePreview(formid, html) {
    cw.log('inline preview');
    var $form = jQuery('#' + formid);
    var $preview = jQuery('#preview_div');
    if  ($preview.length > 0) {
      var preview = $preview[0];
    } else {
      var preview = DIV({id:'preview_div'});
      $form.append(preview);
    }
    if (jQuery.browser.mozilla) {
          preview.innerHTML = html;
    }
    else {
        jQuery(preview).html(html);
    }
    unfreezeFormButtons(formid);
    _clearPreviousErrors(formid);
}

function rePostFormForPreview(formid, html) {
    cw.log('rePostFormForPreview, passing html');
    unfreezeFormButtons(formid);
    _clearPreviousErrors(formid);
    var form = cw.getNode(formid);
    var htmlchild = form.appendChild(INPUT({
            type: 'hidden',
            name: '__preview_html',
            value: html
        }));
    cw.log('preview in new tab');
    var formtarget = form.target;
    form.target = '_blank';
    postForm('__action_preview', 'button_preview', formid);
    form.target = formtarget;
    jQuery(htmlchild).remove();
    unfreezeFormButtons(formid);
    _clearPreviousErrors(formid);
}

