frappe.listview_settings['DSC Sales Invoice'] = {
	get_indicator: function(doc) {
		var colors = {
			"Pending": "orange",
			"Partially Signed": "blue",
			"Completed": "green",
      "Cancelled": "red"
		};
		return [__(doc.status), colors[doc.status], "status,=," + doc.status];
	}
};
 