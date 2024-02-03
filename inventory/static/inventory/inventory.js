/**
 * Script for Dynamic Dropdown Population in Inventory Management System.
 * 
 * Utilizes jQuery to implement cascading dropdown behavior in a web application form. 
 * This script dynamically populates the options of GL Level 2, GL Level 3, and Product dropdowns 
 * based on the user's selections in preceding dropdowns to ensure a coherent selection flow.
 * 
 * Features:
 * - Cascading dropdowns: GL Level 2 and GL Level 3 options are updated based on GL Level 1 selection. 
 *   Product options are updated based on GL Level 3 selection.
 * - AJAX calls: Fetches the relevant options for each dropdown from the server without reloading the page.
 * - User experience: Enhances form usability by ensuring that users can only select from relevant options at each step.
 * 
 * Dependencies: jQuery library.
 */

$(document).ready(function() {
    // Handle change in GL Level 1 dropdown to update GL Level 2 options.
    $('#gl-level-1').change(function() {
        var gl1_id = $(this).val();
        // Initially reset all subsequent dropdowns to a default state.
        $('#gl-level-2, #gl-level-3, #product').html('<option value="">-- Select an Option --</option>').prop('disabled', true);

        if (gl1_id) {
            $.ajax({
                url: '/get_gl_level_2/',
                data: {'gl1_id': gl1_id},
                success: function(data) {
                    console.log(data); // Add this line
                    // Build options for the GL Level 2 dropdown from the AJAX response.
                    var options = '<option value="">-- Select GL Level 2 --</option>';
                    $.each(data, function(index, item) {
                        options += '<option value="' + item.id + '">' + item.name + '</option>';
                    });
                    // Update the GL Level 2 dropdown with the new options.
                    $('#gl-level-2').html(options).prop('disabled', false);
                }
            });
        }
    });

    // Handle change in GL Level 2 dropdown to update GL Level 3 options.
    $('#gl-level-2').change(function() {
        var gl2_id = $(this).val();
        // Reset GL Level 3 and Product dropdowns to ensure only relevant options are shown.
        $('#gl-level-3, #product').html('<option value="">-- Select an Option --</option>').prop('disabled', true);

        if (gl2_id) {
            $.ajax({
                url: '/get_gl_level_3/',
                data: {'gl2_id': gl2_id},
                success: function(data) {
                    console.log(data); // Add this line
                    // Build options for GL Level 3 dropdown.
                    var options = '<option value="">-- Select GL Level 3 --</option>';
                    $.each(data, function(index, item) {
                        options += '<option value="' + item.id + '">' + item.name + '</option>';
                    });
                    // Populate GL Level 3 dropdown with relevant options.
                    $('#gl-level-3').html(options).prop('disabled', false);
                }
            });
        }
    });

    // Handle change in GL Level 3 dropdown to update Product options.
    $('#gl-level-3').change(function() {
        var gl3_id = $(this).val();
        // Ensure Product dropdown is reset for a new selection.
        $('#product').html('<option value="">-- Select a Product --</option>').prop('disabled', true);

        if (gl3_id) {
            $.ajax({
                url: '/get_products/',
                data: {'gl3_id': gl3_id},
                success: function(data) {
                    console.log(data); // Add this line
                    // Build options for the Product dropdown.
                    var options = '<option value="">-- Select a Product --</option>';
                    $.each(data, function(index, item) {
                        options += '<option value="' + item.id + '">' + item.name + '</option>';
                    });
                    // Update Product dropdown with options based on GL Level 3 selection.
                    $('#product').html(options).prop('disabled', false);
                }
            });
        }
    });
});
