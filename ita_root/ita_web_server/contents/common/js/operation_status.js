////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / status.js
//
//   -----------------------------------------------------------------------------------------------
//
//   Copyright 2022 NEC Corporation
//
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.
//
////////////////////////////////////////////////////////////////////////////////////////////////////

class Status {
/*
##################################################
   Constructor
   menu: メニューREST名
   id: 作業実行ID
##################################################
*/
constructor( menu, id, config ) {
    const op = this;
    
    op.menu = menu;
    op.id = id;
    op.config = config;
    
}
/*
##################################################
   画面表示用ID作成
##################################################
*/
viewId( id, sharpFlag = true ) {
    const viewId = ( this.id )? this.id: 'new-conductor';
    return `${( sharpFlag )? `#`: ``}op-${viewId}-${id}`;
}
/*
##################################################
   REST API URL
##################################################
*/
setRestApiUrls() {
    const op = this;
    
    op.rest = {};
    if ( op.id ) {
        op.rest.info = `/menu/${op.menu}/driver/${op.id}/`;
        op.rest.scram = `/menu/${op.menu}/driver/${op.id}/scram/`;
    }
}
/*
##################################################
   定数
##################################################
*/
static string = {
    status: {
    },
    check_operation_status_ansible_role: {
        movementType: 'Ansible Legacy Role',
        movementGem: 'ALR',
        movementClassName: 'node-ansible-legacy-role',
        movementListMenu: 'movement_list_ansible_role',
        targetHostMenu: 'target_host_ansible_role',
        substValueMenu: 'subst_value_list_ansible_role'
    }
}
/*
##################################################
   Setup conductor
##################################################
*/
setup() {
    const op = this;
    
    op.$ = {};
    op.$.operation = $('#operationStatus').find('.sectionBody');
    op.$.executeLog = $('#executeLog').find('.sectionBody');
    op.$.errorLog = $('#errorLog').find('.sectionBody');
    
    op.setRestApiUrls();
    
    if ( op.rest.info ) {
        history.replaceState( null, null, `?menu=${op.menu}&execution_no=${op.id}`);
        fn.fetch( op.rest.info ).then(function( info ){
            op.info = info;
            op.operationStatusInit();
            op.operationStatus();
            op.errorLogInit();
            
            // status_monitoring_cycleごとに更新
            op.monitoring();
            
        }).catch(function( error ){
            op.operationStatusInit();
            op.operationMessage();
            op.errorLogInit();
            console.error( error )
            alert( error.message );
        });
    } else {
        history.replaceState( null, null, `?menu=${op.menu}`);
        op.operationStatusInit();
        op.operationMessage();
        op.errorLogInit();
    }
}
/*
##################################################
   一定間隔で画面更新
##################################################
*/
monitoring() {
    const op = this;
    
    const cycle = fn.cv( op.info.status_monitoring_cycle, 3000 );
    
    setTimeout( function(){
        fn.fetch( op.rest.info ).then(function( info ){
            op.info = info;

            // 更新
            op.operationStatusUpdate();
            op.executeLogUpdate();
            op.errorLogUpdate();
            
            // 完了、完了(異常)、想定外エラー、緊急停止、予約取消の場合は更新しない
            const stopId = [ 5, 6, 7, 8, 10 ];

            if ( stopId.indexOf( op.info.status_id ) === -1 ) {
                op.monitoring();
            }
        }).catch(function( error ){
            console.error( error )
            alert( error.message );
        });
        
    }, cycle );
}
/*
##################################################
   Operation status init
##################################################
*/
operationStatusInit() {
    const op = this;
    
    const html = `<div class="operationStatusContainer"></div>`;
    
    const menu = {
        Main: [
            { input: { className: 'operationId', value: op.id, before: getMessage.FTE05001 } },
            { button: { icon: 'check', text: getMessage.FTE05002, type: 'check', action: 'default', width: '200px'} },
            { button: { icon: 'cal_off', text: getMessage.FTE05003, type: 'cansel', action: 'default', width: '200px'}, display: 'none', separate: true },
            { button: { icon: 'stop', text: getMessage.FTE05004, type: 'scram', action: 'danger', width: '200px'}, display: 'none', separate: true }
        ],
        Sub: []
    };
    op.$.operation.html( fn.html.operationMenu( menu ) + html );
    op.$.operationMenu = op.$.operation.find('.operationMenu');
    op.$.operationContainer = op.$.operation.find('.operationStatusContainer');
    
    const $operationNoInput = op.$.operationMenu.find('.operationMenuInput'),
          $operationNoButton = op.$.operationMenu.find('.operationMenuButton[data-type="check"]');
    $operationNoInput.on('input', function(){
        const value = $operationNoInput.val();
        if ( value !== '') {
            $operationNoButton.prop('disabled', false );
        } else {
            $operationNoButton.prop('disabled', true );
        }
    });
    if ( !op.id ) {
        $operationNoButton.prop('disabled', true );
    }
    
    // メニューボタン
    op.$.operationMenu.find('.operationMenuButton').on('click', function(){
        const $button = $( this ),
              type = $button.attr('data-type');
        switch ( type ) {
            // 作業状態確認切替
            case 'check':
                const value = op.$.operationMenu.find('.operationMenuInput').val();
                fn.clearCheckOperation( op.id );
                fn.createCheckOperation( op.menu, value );
            break;
            // 予約取消
            // 緊急停止
        }
    });
}
/*
##################################################
   Operation message
##################################################
*/
operationMessage() {
    const op = this;
    
    const html = `<div class="contentMessage">
        <div class="contentMessageInner">
            <span class="icon icon-circle_info"></span>` + getMessage.FTE05005 + `<br>
            ` + getMessage.FTE05006 + `<br>
            <a href="?menu=execution_list_ansible_role">` + getMessage.FTE05007 + `</a>` + getMessage.FTE05008 + `
        </div>
    </div>`;
    
    op.$.operationContainer.html( html );
}
/*
##################################################
   Operation menu check
##################################################
*/

/*
##################################################
   Operation status
##################################################
*/
operationStatus() {
    const op = this;
    
    const html = `
    <div class="commonSection">
        <div class="commonBlock">
            <div class="commonTitle">` + getMessage.FTE05009 + `</div>
            <div class="commonBody">
                <table class="commonTable">
                    <tbody class="commonTbody">
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05001 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="execution_no"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05010 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="execution_type"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05011 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="status"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05012 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="execution_engine"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05013 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="caller_conductor"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05014 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="execution_user"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05015 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="populated_data"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05016 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="result_data"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="commonSubTitle">` + getMessage.FTE05017 + `</div>
            <div class="commonBody">
                <table class="commonTable">
                    <tbody class="commonTbody">
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05018 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="scheduled_date_time"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05019 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="start_date_time"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05020 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="end_date_time"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="commonTitle">` + getMessage.FTE05021 + `</div>
            <div class="commonBody">
                <table class="commonTable">
                    <tbody class="commonTbody">
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05022 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="operation_id"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05023 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="operation_name"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="commonBody">
                <ul class="commonMenuList">
                    <li class="commonMenuItem">
                        ${fn.html.iconButton('detail', getMessage.FTE05024, 'hostButton commonButton itaButton', { type: 'host', action: 'default', style: 'width:100%', disabled: 'disabled'})}
                    </li>
                    <li class="commonMenuItem">
                        ${fn.html.iconButton('detail', getMessage.FTE05025, 'valueButton commonButton itaButton', { type: 'value', action: 'default', style: 'width:100%', disabled: 'disabled'})}
                    </li>
                </ul>
            </div>
        </div>
        <div class="commonBlock">
            <div class="commonTitle">` + getMessage.FTE05026 + `</div>
            <div class="movementArea" data-mode="">
                <div class="movementAreaInner">
                    <div class="node ${Status.string[op.menu].movementClassName}">
                        <div class="node-main">
                            <div class="node-terminal node-in connected">
                                <span class="connect-mark"></span>
                                <span class="hole">
                                    <span class="hole-inner"></span>
                                </span>
                            </div>
                            <div class="node-body">
                                <div class="node-circle">
                                    <span class="node-gem">
                                        <span class="node-gem-inner">${Status.string[op.menu].movementGem}</span>
                                    </span>
                                    <span class="node-running"></span>
                                    <span class="node-result"></span>
                                </div>
                                <div class="node-type">
                                    <span>${Status.string[op.menu].movementType}</span>
                                </div>
                                <div class="node-name">
                                    <span class="operationStatusData" data-type="movement_name"></span>
                                </div>
                            </div>
                            <div class="node-terminal node-out connected">
                                <span class="connect-mark"></span>
                                <span class="hole">
                                    <span class="hole-inner"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="commonBody">
                <table class="commonTable">
                    <tbody class="commonTbody">
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05022 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="movement_id"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05023 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="movement_name"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05027 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="delay_timer"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="commonBody">
                <ul class="commonMenuList">
                    <li class="commonMenuItem">
                        ${fn.html.iconButton('detail', getMessage.FTE05028, 'commonButton itaButton', { type: 'movement', action: 'default', style: 'width:100%'})}
                    </li>
                </ul>
            </div>
            <div class="commonSubTitle">` + getMessage.FTE05029 + `</div>
            <div class="commonBody">
                <table class="commonTable">
                    <tbody class="commonTbody">
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05030 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="host_specific_format"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05031 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="winrm_connection"></span></td>
                        </tr>
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05032 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="ansible_cfg"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="commonSubTitle">` + getMessage.FTE05033 + `</div>
            <div class="commonBody">
                <table class="commonTable">
                    <tbody class="commonTbody">
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05034 + `</th>
                            <td class="commonTd"><span class="operationStatusData" data-type="ansible_core_virtualenv"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="commonSubTitle">` + getMessage.FTE05035 + `</div>
            <div class="commonBody">
                <table class="commonTable">
                    <tbody class="commonTbody">
                        <tr class="commonTr">
                            <th class="commonTh">` + getMessage.FTE05036 + `</th>
                            <td class="commonTd"><span class="commonData" data-type="execution_environment"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>`;
    
    op.$.operationContainer.html( html );
    
    op.$.movementArea = op.$.operationContainer.find('.movementArea');
    op.$.node = op.$.operationContainer.find('.node');
    
    // コンテンツボタン
    op.$.operationContainer.find('.commonButton').on('click', function(){
        const $button = $( this ),
              type = $button.attr('data-type'),
              target = { iframeMode: 'tableViewOnly'};
        switch ( type ) {
            case 'movement': {
                const movementId = fn.cv( op.info.execution_list.parameter.movement_id, '');
                target.title = getMessage.FTE05028;
                target.menu = Status.string[ op.menu ].movementListMenu;
                target.filter = { movement_id: { NORMAL: movementId } };
            } break;
            case 'host':
                target.title = getMessage.FTE05024;
                target.menu = Status.string[ op.menu ].targetHostMenu;
                target.filter = { item_no: { NORMAL: op.id } };
            break;
            case 'value':
                target.title = getMessage.FTE05025;
                target.menu = Status.string[ op.menu ].substValueMenu;
                target.filter = { item_no: { NORMAL: op.id } };
            break;
        }
        fn.modalIframe( target.menu, target.title, { filter: target.filter, iframeMode: target.iframeMode });
    });
    
    // ノードのアニメーション完了時
    op.$.node.find('.node-result').on('animationend', function(){
        if ( op.$.node.is('.complete') ) {
            $( this ).off('animationend').addClass('animationEnd');
        }
    });
    
    if ( op.info ) {
        op.operationStatusUpdate();
    }
}
/*
##################################################
   Operation status 更新
##################################################
*/
operationStatusUpdate() {
    const op = this;
    
    // 値を更新する
    for( const key in op.info.execution_list.parameter ) {
        const value = op.info.execution_list.parameter[ key ];
        if ( value ) {
            const $data = op.$.operationContainer.find(`.operationStatusData[data-type="${key}"]`),
                  currentValue = $data.eq(0).text();
            // 変更がある場合のみ内容を更新する
            if ( $data.length && currentValue !== value ) {
                $data.text( value );
            }
        }
    }
    
    /* ステータス
    01 未実行
    02 準備中
    03 実行中
    04 実行中(遅延)
    05 完了
    06 完了(異常)
    07 想定外エラー
    08 緊急停止
    09 未実行(予約)
    10 予約取消
    */
    
    // ホスト確認、代入値確認ボタン
    if ( ['1', '2', '10'].indexOf( op.info.status_id ) === -1 ) {
        op.$.operationContainer.find('.hostButton, .valueButton').prop('disabled', false );
    } else {
        op.$.operationContainer.find('.hostButton, .valueButton').prop('disabled', true );
    }
    
    // ノードの状態を更新する
    switch ( op.info.status_id ) {
        case '3': case '4':
            op.$.node.addClass('running');
        break;
        // 正常終了
        case '5':
            op.$.movementArea.attr('data-result', 'done');
            op.$.node.addClass('complete').find('.node-result').attr('data-result-text', 'DONE');
        break;
        // エラー終了
        case '6':
        case '7':
            op.$.movementArea.attr('data-result', 'error');
            op.$.node.addClass('complete').find('.node-result').attr('data-result-text', 'ERROR');
        break;
        // 緊急停止
        case '8':
            op.$.node.addClass('complete').find('.node-result').attr('data-result-text', 'STOP');
        break;
        // 予約取消
        case '10':
            op.$.node.addClass('complete').find('.node-result').attr('data-result-text', 'CANCEL');
        break;
    }
    
}
/*
##################################################
   Execute log
##################################################
*/
executeLogInit() {
    const op = this;
    op.execute = new Log();
    op.$.executeLog.html( op.execute.setup() );
}
executeLogUpdate() {
    
}
/*
##################################################
   Error log
##################################################
*/
errorLogInit() {
    const op = this;    
    op.errorLog = new Log( );
    op.$.errorLog.html( op.errorLog.setup() );
    op.errorLogUpdate();
}
errorLogUpdate() {
    const op = this;
    
    // エラーログがあるか？
    if ( op.info && op.info.execution_log && op.info.execution_log.error_log ) {
        op.errorLog.update( op.info.execution_log.error_log );
    }
}

}