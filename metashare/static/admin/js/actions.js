(function (a) {
    a.fn.actions = function (h) {
        var b = a.extend({}, a.fn.actions.defaults, h), e = a(this), f = false; checker = function (c) { c ? showQuestion() : reset(); a(e).attr("checked", c).parent().parent().toggleClass(b.selectedClass, c) }; updateCounter = function () {
            var c = a(e).filter(":checked").length; a(b.counterContainer).html(interpolate(ngettext("%(sel)s of %(cnt)s selected", "%(sel)s of %(cnt)s selected", c), { sel: c, cnt: _actions_icnt }, true)); a(b.allToggle).attr("checked", function () {
                if (c == e.length) { value = true; showQuestion() } else {
                    value =
                    false; clearAcross()
                } return value
            })
        }; showQuestion = function () { a(b.acrossClears).hide(); a(b.acrossQuestions).show(); a(b.allContainer).hide() }; showClear = function () { a(b.acrossClears).show(); a(b.acrossQuestions).hide(); a(b.actionContainer).toggleClass(b.selectedClass); a(b.allContainer).show(); a(b.counterContainer).hide() }; reset = function () { a(b.acrossClears).hide(); a(b.acrossQuestions).hide(); a(b.allContainer).hide(); a(b.counterContainer).show() }; clearAcross = function () { reset(); a(b.acrossInput).val(0); a(b.actionContainer).removeClass(b.selectedClass) };
        a(b.counterContainer).show(); a(this).filter(":checked").each(function () { a(this).parent().parent().toggleClass(b.selectedClass); updateCounter(); a(b.acrossInput).val() == 1 && showClear() }); a(b.allToggle).show().click(function () { checker(a(this).attr("checked")); updateCounter() }); a("div.actions span.question a").click(function (c) { c.preventDefault(); a(b.acrossInput).val(1); showClear() }); a("div.actions span.clear a").click(function (c) {
            c.preventDefault(); a(b.allToggle).attr("checked", false); clearAcross(); checker(0);
            updateCounter()
        }); lastChecked = null; a(e).click(function (c) {
            if (!c) c = window.event; var d = c.target ? c.target : c.srcElement; if (lastChecked && a.data(lastChecked) != a.data(d) && c.shiftKey == true) { var g = false; a(lastChecked).attr("checked", d.checked).parent().parent().toggleClass(b.selectedClass, d.checked); a(e).each(function () { if (a.data(this) == a.data(lastChecked) || a.data(this) == a.data(d)) g = g ? false : true; g && a(this).attr("checked", d.checked).parent().parent().toggleClass(b.selectedClass, d.checked) }) } a(d).parent().parent().toggleClass(b.selectedClass,
                d.checked); lastChecked = d; updateCounter()
        }); a("form#changelist-form table#result_list tr").find("td:gt(0) :input").change(function () { f = true }); a('form#changelist-form button[name="index"]').click(function () { if (f) return confirm(gettext("You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.")) }); a('form#changelist-form input[name="_save"]').click(function () {
            var c = false; a("div.actions select option:selected").each(function () {
                if (a(this).val()) c =
                    true
            }); if (c) return f ? confirm(gettext("You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.")) : confirm(gettext("You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button."))
        })
    }; a.fn.actions.defaults = {
        actionContainer: "div.actions", counterContainer: "span.action-counter", allContainer: "div.actions span.all", acrossInput: "div.actions input.select-across",
        acrossQuestions: "div.actions span.question", acrossClears: "div.actions span.clear", allToggle: "#action-toggle", selectedClass: "selected"
    }
})(django.jQuery);
