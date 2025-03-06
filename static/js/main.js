// データベース情報を取得して表示
function fetchDatabaseInfo() {
    $('.loading').show();
    $('#database-info').hide();
    
    $.get('/tables', function(data) {
        const container = $('#database-info');
        container.empty();
        
        for (const dbName in data) {
            const dbInfo = data[dbName];
            const dbDiv = $('<div class="database-card">');
            
            // データベースヘッダー
            const dbHeader = $('<div class="database-header" data-bs-toggle="collapse">');
            dbHeader.append(`
                <div class="d-flex justify-content-between align-items-center">
                    <h2 class="h4 mb-0">
                        <i class="fas fa-database me-2"></i>${dbName}
                    </h2>
                    <i class="fas fa-chevron-down icon-toggle"></i>
                </div>
            `);
            
            // データベースコンテンツ
            const dbContent = $('<div class="database-content collapse">');

            if (dbInfo.error) {
                dbContent.append(`<p class="text-danger"><i class="fas fa-exclamation-circle me-2"></i>${dbInfo.error}</p>`);
            } else {
                for (const tableName in dbInfo.tables) {
                    const tableInfo = dbInfo.tables[tableName];
                    const tableDiv = $('<div class="table-section">');
                    
                    // テーブルヘッダー
                    const tableHeader = $('<div class="table-header">');
                    tableHeader.append(`
                        <div class="d-flex justify-content-between align-items-center">
                            <h3 class="h5 mb-0">
                                <i class="fas fa-table me-2"></i>${tableName}
                                <small class="text-muted ms-2">${tableInfo.rows ? tableInfo.rows.length : 0} 行</small>
                            </h3>
                            <i class="fas fa-chevron-right icon-toggle"></i>
                        </div>
                    `);
                    
                    // テーブルコンテンツ
                    const tableContent = $('<div class="table-content">');

                    if (tableInfo.error) {
                        tableContent.append(`<p class="text-danger"><i class="fas fa-exclamation-circle me-2"></i>${tableInfo.error}</p>`);
                    } else {
                        const table = $('<table class="table table-hover">');
                        
                        // ヘッダー行
                        const thead = $('<thead>');
                        const headerRow = $('<tr>');
                        tableInfo.columns.forEach(column => {
                            headerRow.append(`<th>${column}</th>`);
                        });
                        thead.append(headerRow);
                        table.append(thead);

                        // データ行
                        const tbody = $('<tbody>');
                        tableInfo.rows.forEach(row => {
                            const tr = $('<tr>');
                            tableInfo.columns.forEach(column => {
                                tr.append(`<td>${row[column]}</td>`);
                            });
                            tbody.append(tr);
                        });
                        table.append(tbody);

                        tableContent.append(table);
                    }
                    
                    tableDiv.append(tableHeader, tableContent);
                    dbContent.append(tableDiv);
                }
            }
            
            dbDiv.append(dbHeader, dbContent);
            container.append(dbDiv);
        }
        
        $('.loading').hide();
        container.show();
        
        // テーブルの開閉
        $('.table-header').click(function() {
            const content = $(this).next('.table-content');
            const icon = $(this).find('.icon-toggle');
            content.slideToggle();
            icon.toggleClass('rotated');
        });
        
        // データベースの開閉
        $('.database-header').click(function() {
            const content = $(this).next('.database-content');
            const icon = $(this).find('.icon-toggle');
            content.collapse('toggle');
            icon.toggleClass('rotated');
        });
    });
}

// 初期ロード
$(document).ready(function() {
    fetchDatabaseInfo();
});
