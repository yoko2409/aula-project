$(document).ready(function () {
    $("#add-choice").click(function () {
        // Clone the last choice form and append it to the formset
        var lastFormRow = $("#formset .formset-row:last");
        var newFormRow = lastFormRow.clone();

        // Update id and name attributes for input fields
        newFormRow.find("input").each(function () {
            $(this).attr("id", function (_, id) {
                return id.replace(/\d+/, function (match) {
                    return parseInt(match) + 1;
                });
            }).attr("name", function (_, name) {
                return name.replace(/\d+/, function (match) {
                    return parseInt(match) + 1;
                });
            }).val("");  // Clear the input field
        });

        // Append the modified cloned form to the formset
        $("#formset").append(newFormRow);
    });
});
