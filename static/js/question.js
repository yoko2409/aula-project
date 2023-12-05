document.addEventListener('DOMContentLoaded', function () {
    const formsetContainer = document.querySelector("#formset");

    function updateElementIndex(el, prefix, index) {
        var idRegex = new RegExp('(' + prefix + '-\\d+-)');
        var replacement = prefix + '-' + index + '-';
        if (el.id) el.id = el.id.replace(idRegex, replacement);
        if (el.name) el.name = el.name.replace(idRegex, replacement);
        if (el.htmlFor) el.htmlFor = el.htmlFor.replace(idRegex, replacement);
    }

    function addNewTextField() {
        // TOTAL_FORMS要素のセレクタが正しいことを確認してください
        var totalForms = document.querySelector("#id_choices-TOTAL_FORMS");
        console.log(totalForms);
        if (!totalForms) {
            console.error('TOTAL_FORMS element not found');
            return;
        }
        var formNum = parseInt(totalForms.value);
        var newForm = document.querySelector('.formset-row').cloneNode(true);

        var newFormFields = newForm.querySelectorAll('input, label, select, textarea');
        newFormFields.forEach(function(field){
            updateElementIndex(field, 'choices', formNum);
            if (field.tagName === 'INPUT' && field.type === 'text') {
                field.value = '';
            }
        });

        formsetContainer.appendChild(newForm);
        totalForms.setAttribute('value', `${formNum + 1}`);

        // Add focusin event to the new form
        newForm.querySelector('input[type="text"]').addEventListener('focusin', function (event) {
            addNewTextField();
        });
    }

    formsetContainer.addEventListener('focusin', function (event) {
        var lastInput = formsetContainer.lastElementChild.querySelector('input[type="text"]');
        if (event.target === lastInput) {
            addNewTextField();
        }
    }, true);
});
