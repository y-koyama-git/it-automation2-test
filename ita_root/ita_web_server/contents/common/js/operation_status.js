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
        }).catch(function( error ){
            op.operationStatusInit();
            op.operationMessage();
            alert( error.message );
        });
    } else {
        history.replaceState( null, null, `?menu=${op.menu}`);
        op.operationStatusInit();
        op.operationMessage();
    }
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
            { input: { className: 'operationId', value: op.id, before: '作業No.' } },
            { button: { icon: 'check', text: '作業状態確認', type: 'check', action: 'default', width: '200px'} },
            { button: { icon: 'cal_off', text: '予約取消', type: 'cansel', action: 'default', width: '200px'}, display: 'none', separate: true },
            { button: { icon: 'stop', text: '緊急停止', type: 'scram', action: 'danger', width: '200px'}, display: 'none', separate: true }
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
            <span class="icon icon-circle_info"></span>作業No.が未設定です。<br>
            作業No.を入力し作業状態確認ボタンを押下するか、<br>
            <a href="?menu=execution_list_ansible_role">作業管理ページ</a>にて詳細ボタンを押下してください。
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
    <div class="operationStatusSection">
        <div class="operationStatusBlock">
            <div class="operationStatusTitle">作業ステータス</div>
            <div class="operationStatusBody">
                <table class="operationStatusTable">
                    <tbody class="operationStatusTbody">
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">作業No.</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="execution_no"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">実行種別</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="execution_type"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">ステータス</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="status"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">実行エンジン</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="execution_engine"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">呼出元Conductor</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="caller_conductor"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">実行ユーザ</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="execution_user"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">投入データ</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="populated_data"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">結果データ</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="result_data"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="operationStatusSubTitle">作業状況</div>
            <div class="operationStatusBody">
                <table class="operationStatusTable">
                    <tbody class="operationStatusTbody">
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">予約日時</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="scheduled_date_time"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">開始日時</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="start_date_time"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">終了日時</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="end_date_time"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="operationStatusTitle">オペレーション</div>
            <div class="operationStatusBody">
                <table class="operationStatusTable">
                    <tbody class="operationStatusTbody">
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">ID</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="operation_id"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">名称</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="operation_name"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="operationStatusBody">
                <ul class="operationStatusMenuList">
                    <li class="operationStatusMenuItem">
                        ${fn.html.iconButton('detail', '作業対象ホスト確認', 'operationStatusButton itaButton', { type: 'host', action: 'default', style: 'width:100%'})}
                    </li>
                    <li class="operationStatusMenuItem">
                        ${fn.html.iconButton('detail', '代入値確認', 'operationStatusButton itaButton', { type: 'value', action: 'default', style: 'width:100%'})}
                    </li>
                </ul>
            </div>
        </div>
        <div class="operationStatusBlock">
            <div class="operationStatusTitle">Movement</div>
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
            <div class="operationStatusBody">
                <table class="operationStatusTable">
                    <tbody class="operationStatusTbody">
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">ID</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="movement_id"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">名称</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="movement_name"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">遅延タイマー（分）</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="delay_timer"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="operationStatusBody">
                <ul class="operationStatusMenuList">
                    <li class="operationStatusMenuItem">
                        ${fn.html.iconButton('detail', 'Movement詳細確認', 'operationStatusButton itaButton', { type: 'movement', action: 'default', style: 'width:100%'})}
                    </li>
                </ul>
            </div>
            <div class="operationStatusSubTitle">Ansible利用情報</div>
            <div class="operationStatusBody">
                <table class="operationStatusTable">
                    <tbody class="operationStatusTbody">
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">ホスト指定形式</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="host_specific_format"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">WinRM接続</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="winrm_connection"></span></td>
                        </tr>
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">ansible.cfg</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="ansible_cfg"></span></td>
                        </tr>
                     </tbody>
                </table>
            </div>
            <div class="operationStatusSubTitle">Ansible Core利用情報</div>
            <div class="operationStatusBody">
                <table class="operationStatusTable">
                    <tbody class="operationStatusTbody">
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">virtualenv</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="ansible_core_virtualenv"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="operationStatusSubTitle">Ansible Automation Controller利用情報</div>
            <div class="operationStatusBody">
                <table class="operationStatusTable">
                    <tbody class="operationStatusTbody">
                        <tr class="operationStatusTr">
                            <th class="operationStatusTh">実行環境</th>
                            <td class="operationStatusTd"><span class="operationStatusData" data-type="execution_environment"></span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>`;
    
    op.$.operationContainer.html( html );
    
    // コンテンツボタン
    op.$.operation.find('.operationStatusButton').on('click', function(){
        const $button = $( this ),
              type = $button.attr('data-type'),
              target = { iframeMode: 'tableViewOnly'};
        switch ( type ) {
            case 'movement': {
                const movementId = fn.cv( op.info.execution_list.parameter.movement_id, '');
                target.title = 'Movement詳細確認';
                target.menu = Status.string[ op.menu ].movementListMenu;
                target.filter = { movement_id: { NORMAL: movementId } };
            } break;
            case 'host':
                target.title = '作業対象ホスト確認';
                target.menu = Status.string[ op.menu ].targetHostMenu;
                target.filter = { item_no: { NORMAL: op.id } };
            break;
            case 'value':
                target.title = '代入値確認';
                target.menu = Status.string[ op.menu ].substValueMenu;
                target.filter = { item_no: { NORMAL: op.id } };
            break;
        }
        fn.modalIframe( target.menu, target.title, { filter: target.filter, iframeMode: target.iframeMode });
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
operationStatusUpdate( updateData ) {
    const op = this;
    
    for( const key in op.info.execution_list.parameter ) {
        const value = op.info.execution_list.parameter[ key ];
        if ( value ) {
            const $data = op.$.operationContainer.find(`.operationStatusData[data-type="${key}"]`),
                  currentValue = $data.text();
            // 変更がある場合のみ内容を更新する
            if ( currentValue !== value ) {
                $data.text( value );
            }
        }
    }
    /*
    op.info.execution_list.parameter
    
    op.$.operation.find('.node');
    */
}
/*
##################################################
   Execute log
##################################################
*/
executeLog() {
    const menu = {
        Main: [
            { input: { className: 'operationId', value: op.id, before: 'ログ検索' } },
            { button: { icon: 'check', text: '作業状態確認', type: 'check', action: 'default', width: '200px'} },
            { button: { icon: 'cal_off', text: '予約取消', type: 'cansel', action: 'default', width: '200px'}, display: 'none', separate: true },
            { button: { icon: 'stop', text: '緊急停止', type: 'scram', action: 'danger', width: '200px'}, display: 'none', separate: true }
        ],
        Sub: []
    };
    op.$.operation.html( fn.html.operationMenu( menu ) + html );
}
/*
##################################################
   Error log
##################################################
*/
errorLog() {

}

}