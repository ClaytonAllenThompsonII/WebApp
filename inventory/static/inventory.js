/**
 * Script for managing cascading dropdowns in a web application.
 * This script handles the dynamic population of GL Level 2 and GL Level 3 dropdowns
 * based on the selection made in the preceding dropdown. It also manages the population
 * of a products dropdown based on the selection in the GL Level 3 dropdown.
 * Dependencies: jQuery
 */

// This script manages cascading dropdowns for GL levels and products.

$(document).ready(function() {
    // Event listener for change in GL Level 1 dropdown.
    $('#gl-level-1').change(function() {
        var gl1_id = $(this).val();
        // Reset the following dropdowns when GL Level 1 changes.
        $('#gl-level-2, #gl-level-3, #type').html('<option value="">-- Select an Option --</option>').prop('disabled', true);

        // If a GL Level 1 item is selected, fetch GL Level 2 items.
        if (gl1_id) {
            $.ajax({
                url: '/get_gl_level_2/', // Endpoint for GL Level 2 data.
                data: {'gl1_id': gl1_id}, // Data to be sent to the server.
                success: function(data) {
                    // Populate GL Level 2 dropdown with data from the server.
                    $('#gl-level-2').html(data).prop('disabled', false);
                }
            });
        }
    });

    // Event listener for change in GL Level 2 dropdown.
    $('#gl-level-2').change(function() {
        var gl2_id = $(this).val();
        // Reset GL Level 3 and Product dropdowns when GL Level 2 changes.
        $('#gl-level-3, #type').html('<option value="">-- Select an Option --</option>').prop('disabled', true);

        // If a GL Level 2 item is selected, fetch GL Level 3 items.
        if (gl2_id) {
            $.ajax({
                url: '/get_gl_level_3/', // Endpoint for GL Level 3 data.
                data: {'gl2_id': gl2_id}, // Data to be sent to the server.
                success: function(data) {
                    // Populate GL Level 3 dropdown with data from the server.
                    $('#gl-level-3').html(data).prop('disabled', false);
                }
            });
        }
    });

    // Event listener for change in GL Level 3 dropdown.
    $('#gl-level-3').change(function() {
        var gl3_id = $(this).val();
        // Reset Product dropdown when GL Level 3 changes.
        $('#type').html('<option value="">-- Select a Product --</option>').prop('disabled', true);

        // If a GL Level 3 item is selected, fetch Product items.
        if (gl3_id) {
            $.ajax({
                url: '/get_products/', // Endpoint for product data.
                data: {'gl3_id': gl3_id}, // Data to be sent to the server.
                success: function(data) {
                    // Populate Product dropdown with data from the server.
                    $('#type').html(data).prop('disabled', false);
                }
            });
        }
    });
});
