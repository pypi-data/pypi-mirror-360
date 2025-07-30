/**
 * Integration code for the multi-database jqGrid implementation
 */

// Define button configuration in a central location
window.jqGridButtonConfig = {
    // Default buttons for all tables
    defaultButtons: [
        {
            id: 'refresh',
            label: 'Refresh',
            icon: 'fa-sync-alt',
            class: 'btn-outline-primary'
        },
        {
            id: 'clear-filters',
            label: 'Clear Filters',
            icon: 'fa-filter',
            class: 'btn-outline-secondary'
        },
        {
            id: 'save-filter',
            label: 'Save Filter',
            icon: 'fa-save',
            class: 'btn-outline-warning'
        },
        {
            id: 'delete-filter',
            label: 'Delete Filter',
            icon: 'fa-trash',
            class: 'btn-outline-danger'
        }
    ],
    
    // Table-specific buttons - can be extended by users
    tableButtons: {
        // Example: buttons for leads table
        lead: [
            {
                id: 'create-campaign',
                label: 'Create Campaign',
                icon: 'fa-comments',
                class: 'btn-info',
                action: function(tableInstance) {
                    if (typeof openFormCard === 'function') {
                        openFormCard({url:'/crud/sales/campaign/', mode:'modal'});
                    }
                }
            }
        ]
    },
    
    // Bulk action buttons - can be extended by users
    bulkActions: {
        // Default bulk actions for all tables
        defaultActions: [
            {
                id: 'bulk-update',
                label: 'Update Selected',
                icon: 'fa-edit',
                class: 'btn-primary'
            },
            {
                id: 'bulk-delete',
                label: 'Delete Selected',
                icon: 'fa-trash',
                class: 'btn-danger'
            }
        ],
        
        // Table-specific bulk actions
        tableActions: {
            lead: [
                {
                    id: 'create-campaign',
                    label: 'Create Campaign',
                    icon: 'fa-comments',
                    class: 'btn-info'
                }
            ]
        }
    }
};

// Example of additional initialization in the document.ready function
(function($) {
    $(document).ready(function() {
        // Add custom hooks to extend grid functionality
        window.jqGridConfig.hooks.beforeCreateToolbar = function(tableInstance, toolbarId, gridConfig) {
            // Check if we have custom buttons for this table
            if (window.jqGridButtonConfig.tableButtons[tableInstance.tableName]) {
                // Add table-specific buttons to options
                const customButtons = window.jqGridButtonConfig.tableButtons[tableInstance.tableName];
                if (!tableInstance.options.customButtons) {
                    tableInstance.options.customButtons = [];
                }
                
                // Add buttons if they don't already exist
                customButtons.forEach(button => {
                    if (!tableInstance.options.customButtons.some(b => b.id === button.id)) {
                        tableInstance.options.customButtons.push(button);
                    }
                });
            }
        };
        
        window.jqGridConfig.hooks.beforeCreateBulkActions = function(tableInstance, bulkActionConfig) {
            // Check if we have custom bulk actions for this table
            const tableBulkActions = window.jqGridButtonConfig.bulkActions.tableActions[tableInstance.tableName];
            if (tableBulkActions && tableBulkActions.length) {
                // Add table-specific bulk actions to configuration
                if (!bulkActionConfig.actions) {
                    bulkActionConfig.actions = [];
                }
                
                // Add actions if they don't already exist
                tableBulkActions.forEach(action => {
                    if (!bulkActionConfig.actions.some(a => a.id === action.id)) {
                        bulkActionConfig.actions.push(action);
                    }
                });
            }
        };
    });
})(jQuery);