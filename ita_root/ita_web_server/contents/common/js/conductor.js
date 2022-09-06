////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / conductor.js
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

class Conductor {
/*
##################################################
   Constructor
##################################################
*/
constructor( target, mode ) {
    const cd = this;
    
    cd.target = target;
    cd.version = '2.0.0';
    
    // Conductor class ID
    cd.id = fn.getParams().conductor_class_id;
    console.log(cd.id)
    
    // 編集モードでIDの指定があれば閲覧モードにする
    if ( mode === 'edit' && ( cd.id !== undefined && cd.id !== '')) {
        cd.mode = 'view';
    } else {
        cd.mode = mode;
    }
}
/*
##################################################
   Setup conductor
##################################################
*/
setup() {
    const cd = this;
    
    const html = `
    <div id="editor" class="load-wait" data-editor-mode="">
        <div class="editor-inner">
            <div id="editor-menu">
                ${cd.operationMenuHtml()}
            </div>
            <div id="editor-header">
                <div id="editor-mode"></div>
                <div class="editor-header-menu">
                    ${cd.headerHtml()}
                </div>
            </div>
            <div id="editor-main">
                <div id="editor-body">
                    <div id="editor-edit" class="editor-block">
                        <div class="editor-block-inner">
                            ${cd.editViewHtml()}
                        </div>
                    </div>
                </div>
                <div id="editor-panel" class="editor-row-resize">
                </div>
            </div>
        </div>
    </div>`;
    
    // jQueryオブジェクトキャッシュ
    cd.$ = {};
    cd.$.window = $( window );
    cd.$.body = $('body');
    cd.$.target = $( cd.target );
    cd.$.editor = $( html );
    cd.$.menu = cd.$.editor.find('#editor-menu');
    cd.$.header = cd.$.editor.find('.editor-header-menu');
    cd.$.panel = cd.$.editor.find('#editor-panel');
    cd.$.mode = cd.$.editor.find('#editor-mode');
    
    cd.$.area = cd.$.editor.find('#canvas-visible-area'),
    cd.$.canvas = cd.$.editor.find('#canvas'),
    cd.$.artBoard = cd.$.editor.find('#art-board');
    
    // HTMLセット
    cd.$.target.html( cd.$.editor );
    
    // 必要なデータの読み込み
    const restApiUrls = ['/menu/conductor_class_edit/conductor/class/info/'];
    if ( cd.id ) {
        restApiUrls.push(`/menu/conductor_class_edit/conductor/class/${cd.id}/`);
    }
    
    fn.fetch( restApiUrls ).then(function( result ){
        cd.init( result[0], result[1] );
    }).catch(function( error ){
        if ( error.message ) {
            alert( error.message + '\nリロードします。' );
            location.href = '?menu=conductor_class_edit';
        }
    });
    
}
/*
##################################################
   Operation menu
##################################################
*/
operationMenuHtml() {
    const menu = {
        edit: [
            { type: 'registration', title: '登録', action: 'positive', width: '200px'},
            { type: 'selectConductor', title: 'Conductor選択', action: 'default', width: '160px', separate: true },
            { type: 'reset', title: 'リセット', action: 'negative', width: '120px'}
        ],
        view: [
            { type: 'edit', title: '編集', action: 'positive', width: '200px'},
            { type: 'selectConductor', title: 'Conductor選択', action: 'default', width: '160px', separate: true },
            { type: 'diversion', title: '流用新規', action: 'normal', width: '160px'},
            { type: 'new', title: '新規', action: 'normal', width: '160px'}
        ],
        update: [
            { type: 'update', title: '更新', action: 'positive', width: '200px'},
            { type: 'refresh', title: '再読み込み', action: 'negative', separate: true, width: '120px'},
            { type: 'cancel', title: 'キャンセル', action: 'negative', width: '120px'},
        ],
        execute: [
            { type: 'execute', title: '作業実行', action: 'positive', width: '200px'},
            { type: 'executeSelectConductor', title: 'Conductor選択', action: 'default', width: '160px', separate: true },
            { type: 'executeSelectOperation', title: 'Operation選択', action: 'default', width: '160px'},
        ],
        checking: [
            { type: 'stop', title: '緊急停止', action: 'danger', width: '200px'},
        ]
    };
    
    const list = [];
    for ( const item of menu[ this.mode ] ) {
        const itemClass = ['operation-menu-item'],
              attr = { action: item.action, menu: item.type };
        if ( item.separate ) itemClass.push('operation-menu-separate');
        if ( item.width ) attr.style = `width:${item.width}`;
        list.push(`<li class="${itemClass.join(' ')}">`
            + fn.html.button( item.title, ['itaButton', 'operation-menu-button'], attr )
        + `</li>`)
    }
    return `
    <ul class="operation-menu-list">
        ${list.join('')}
    </ul>`;
}
/*
##################################################
   Header html
##################################################
*/
headerHtml() {
    const cd = this;
    
    // モードごとに表示するボタンを変更する
    const main = [];
    if ( cd.mode === 'edit' || cd.mode === 'update' || cd.mode === 'view') {
        main.push({ type: 'conductor-save', title: 'JSON保存'});
    }
    if ( cd.mode === 'edit'  || cd.mode === 'update') {
        main.push({ type: 'conductor-read', title: 'JSON読込', separate: true });
        main.push({ type: 'undo', title: '操作取り消し', disabled: true });
        main.push({ type: 'redo', title: '操作やり直し', separate: true, disabled: true });
        main.push({ type: 'node-delete', title: '選択ノード削除', disabled: true });
    }
    main.push({ type: 'view-all', title: '全体表示', separate: true });
    
    const mainItem = [];
    for ( const item of main ) {
        const className = ['editor-menu-button'],
              attr = [`data-menu="${item.type}"`];
        if ( item.separate ) className.push('editor-menu-separate');
        if ( item.disabled ) attr.push('disabled');
        mainItem.push(`<li class="editor-menu-item">`
            + `<button class="${className.join(' ')}" ${attr.join(' ')}>${item.title}</button>`
        + `</li>`);
    }
    
    return `
    <div class="editor-header-main-menu">
        <ul class="editor-menu-list conductor-header-menu1">
            ${mainItem.join('')}
        </ul>
    </div>
    <div class="editor-header-sub-menu">
        <ul class="editor-menu-list">
            <li class="editor-menu-item full-screen-hide"><button class="editor-menu-button" data-menu="full-screen-on">フルスクリーン</button></li>
            <li class="editor-menu-item full-screen-show"><button class="editor-menu-button" data-menu="full-screen-off">フルスクリーン解除</button></li>
        </ul>
    </div>`;
}
/*
##################################################
   View area html
##################################################
*/
editViewHtml() {
    return `
    <div id="canvas-visible-area">
        <div id="canvas">
            <div id="art-board">      
            </div>
        </div>
    </div>

    <!--<div id="editor-display">
        <div id="editor-explanation">
            <dl class="explanation-list">
                <dt class="explanation-term"><span class="mouse-icon mouse-left"></span></dt>
                <dd class="explanation-description"></dd>
                <dt class="explanation-term"><span class="mouse-icon mouse-left"></span></dt>
                <dd class="explanation-description"></dd>
                <dt class="explanation-term"><span class="mouse-icon mouse-wheel"></span></dt>
                <dd class="explanation-description"></dd>
                <dt class="explanation-term"><span class="mouse-icon mouse-right"></span></dt>
                <dd class="explanation-description"></dd>
            </dl>
        </div>
    </div>-->`;
}
/*
##################################################
   Info html
##################################################
*/
infoHtml() {
    return `
    <div class="editor-tab">
        <div class="editor-tab-menu">
            <ul class="editor-tab-menu-list">
                <li class="editor-tab-menu-item" data-tab="log">ログ</li>
            </ul>
        </div>
        <div class="editor-tab-contents">
            <div id="log" class="editor-tab-body">
                <div class="editor-tab-body-inner">
                    <div class="editor-log">
                        <table class="editor-log-table">
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>            
        </div>
    </div>`;
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Init
//
////////////////////////////////////////////////////////////////////////////////////////////////////

init( info, conductorData ) {
    const cd = this;
    
    cd.info = info;
    
    // 設定値
    cd.setting = {
        debug: false,
        setStorage: false
    };
    
    // デバッグモード
    if ( fn.getParams().debug === 'true') cd.setting.debug = true;
    
    // ID 連番用
    cd.count = {
        node: 1,
        terminal: 1,
        edge: 1
    };
    
    // Conductor構造データ
    if ( conductorData ) {
        cd.data = conductorData;
        cd.original = $.extend( true, {}, conductorData );
    } else {
        cd.setInitialConductorData();
    }

    // 読み込み完了
    cd.$.editor.removeClass('load-wait');
    
    // キャンバス初期設定
    cd.initCanvas();   
    
    // SVGエリア初期設定
    cd.initSvgArea();
    
    // パネル初期設定
    cd.initPanel();
    
    // モードセット
    cd.conductorMode( cd.mode );
    
    // ノード初期設定
    cd.initNode();
    
    // 履歴初期設定
    cd.initHistory();
    
    // 初期表示
    if ( cd.mode !== 'execute') {
        if ( conductorData ) {
            if ( cd.mode === 'checking') {
                // 作業確認画面更新イベント登録
                cd.$.window.on('conductorDrawEnd', function(){
                    cd.$.window.off('conductorDrawEnd');
                    cd.conductorStatusUpdate( 0 );
                });
            }
            cd.loadConductor();
        } else if ( fn.storage.check('conductor-edit-temp') ) {
            cd.loadConductor( fn.storage.get('conductor-edit-temp'));
        } else {
            cd.InitialSetNode();
        }
    }
    
    // 基本イベント
    cd.initEvents();    
}
/*
##################################################
   基本初期表示
##################################################
*/
InitialSetNode() {
    const cd = this;
    cd.newNode('start', 'left', 'center');
    cd.newNode('end', 'right', 'center');
    cd.panelConductorReset();
}
/*
##################################################
   Menuボタン制御
##################################################
*/
menuButtonDisabled( disabledFlag ) {
    this.$.menu.find('.operation-menu-button').prop('disabled', disabledFlag );
}
/*
##################################################
   モード切替
##################################################
*/
conductorMode( mode ) {
    const cd = this;

    cd.mode = mode;

    cd.$.editor.attr('data-editor-mode', cd.mode );
    
    // メニュー切替
    cd.$.menu.html( cd.operationMenuHtml() );
    cd.$.header.html( cd.headerHtml() );
    
    // モードテキスト切替
    cd.$.mode.text( cd.mode.toUpperCase() );

    // パネル切替
    cd.select = [];
    cd.panelChange();
}
/*
##################################################
   Conductor構造データの初期化
##################################################
*/
setInitialConductorData() {
    const cd = this;
    
    cd.data = {
        config: {
            'nodeNumber' : cd.count.node,
            'terminalNumber' : cd.count.terminal,
            'edgeNumber' : cd.count.edge,
            'editorVersion': cd.version
        },
        conductor: {
            'id': null,
            'conductor_name': null,
            'last_update_date_time': null,
            'note': null
        }
    };
}
/*
##################################################
   アクションモード
##################################################
*/
setAction( mode ) {
    this.$.body.attr('data-action-mode', mode );
}
clearAction() {
    this.$.body.removeAttr('data-action-mode');
}
checkAction( mode ) {
    return ( mode === this.$.body.attr('data-action-mode') ) ? true : false;
}
/*
##################################################
   メッセージ
##################################################
*/
message( message ) {
}
/*
##################################################
   基本イベント
##################################################
*/
initEvents() {
    const cd = this;
    
    // --------------------------------------------------
    // エディタタブ
    // --------------------------------------------------
    cd.$.editor.find('.editor-tab').each( function() {

        const $tab = $( this ),
              $tabItem = $tab.find('.editor-tab-menu-item'),
              $tabBody = $tab.find('.editor-tab-body');

        $tabItem.eq(0).addClass('selected');
        $tabBody.eq(0).addClass('selected');

        $tabItem.on('click', function() {
          const $clickTab = $( this ),
                $openTab = $('#' + $clickTab.attr('data-tab') );

          $tab.find('.selected').removeClass('selected');
          $clickTab.add( $openTab ).addClass('selected');
        });

    });
    
    // --------------------------------------------------
    // 新規登録時のみ、ページを移動する際に
    // ローカルストレージに保存する
    // --------------------------------------------------
    cd.$.window.on('beforeunload', function(){
        if ( cd.mode === 'edit') {
            cd.saveConductor( cd.data );
        }
    });
    
    // --------------------------------------------------
    // メニューボタン
    // --------------------------------------------------
    cd.$.menu.on('click', '.operation-menu-button ', function(){
      const $button = $( this ),
            type = $button.attr('data-menu');

      cd.nodeDeselect();
      cd.panelChange();

      switch( type ) {
          case 'execute':
              // 実行しますか？
              if ( window.confirm(`実行しますか？`) ) {
                  cd.menuButtonDisabled( true );
                  /*
                      実行処理
                  */
              }
          break;
          case 'registration':
              // 登録しますか？
              if ( window.confirm('登録しますか？') ) {
                  cd.menuButtonDisabled( true );

                  fn.fetch('/menu/conductor_class_edit/conductor/class/maintenance/', null, 'POST', cd.data ).then(function( result ){
                      window.location.href = `?menu=conductor_class_edit&conductor_class_id=${result.conductor_class_id}`;
                  }).catch(function( error ){
                      cd.menuButtonDisabled( false );
                  });
              }
          break;
          case 'selectConductor': {
              cd.menuButtonDisabled( true );
              
              cd.selectConductorModalOpen().then(function( selectId ){
                  if ( selectId ) {
                      window.location.href = `?menu=conductor_class_edit&conductor_class_id=${selectId}`;
                  } else {
                      cd.menuButtonDisabled( false );
                  }
              });
          } break;
          case 'executeSelectConductor': {
              cd.menuButtonDisabled( true );
              
              cd.selectConductorModalOpen().then(function( selectId ){
                  if ( selectId ) {
                      console.log(selectId)
                  }
                  cd.menuButtonDisabled( false );
              });
          } break;
          case 'executeSelectOperation': {
              cd.menuButtonDisabled( true );
              
              cd.selectOperationModalOpen().then(function( selectId ){
                  if ( selectId ) {
                      console.log(selectId)
                  }
                  cd.menuButtonDisabled( false );
              });
          } break;
          case 'edit':
              cd.conductorMode('update');
          break;
          case 'reset':
              if ( window.confirm('リセットしますか？') ) {
                    cd.clearConductor();
                    cd.InitialSetNode();
              }
          break;
          case 'diversion':
            // 流用しますか？
            if ( window.confirm('流用しますか？') ) {
              // 流用する場合は下記の項目はnullに
              cd.data.conductor.id = null;
              cd.data.conductor.last_update_date_time = null;
              cd.data.conductor.conductor_name = null;
              cd.data.conductor.note = null;

              cd.conductorMode('edit');
              cd.panelConductorReset();

              history.replaceState( null, null, '?menu=conductor_class_edit');
            }
            break;
          case 'new':
              cd.clearConductor();
              cd.InitialSetNode();
              
              cd.conductorMode('edit');
              cd.panelConductorReset();

              history.replaceState( null, null, '?menu=conductor_class_edit');
          break;
          case 'update':
              // 更新しますか？
              if ( window.confirm('更新しますか？') ) {
                  cd.menuButtonDisabled( true );

                  fn.fetch(`/menu/conductor_class_edit/conductor/class/maintenance/${cd.id}/`, null, 'PATCH', cd.data ).then(function(result){
                      window.location.href = `?menu=conductor_class_edit&conductor_class_id=${result.conductor_class_id}`;
                  }).catch(function( error ){
                      cd.menuButtonDisabled( false );
                  });

              }
          break;
          case 'refresh':
            // 再読込しますか？
            if ( window.confirm('再読込しますか？') ) {
                //
            }
            break;
          case 'cancel':
            // キャンセル確認無し
            cd.selectConductor( cd.original );
            cd.conductorMode('view');
          break;
          case 'cansel-instance':
            // 予約取消
            if ( window.confirm('予約取消') ) {
              cd.menuButtonDisabled( true );
              //
            }
            break;
          case 'scram-instance':
            // 強制停止
            if ( window.confirm('強制停止') ) {
              clearTimeout( cd.pollingTimerID );
              cd.menuButtonDisabled( true );
              //
            }
            break;
        }
    });
    
    // --------------------------------------------------
    // エディタボタン
    // --------------------------------------------------
    cd.$.header.on('click', '.editor-menu-button', function(){

        const $button = $( this ),
              buttonType = $button.attr('data-menu'),
              buttonDisabledTime = 300;

        switch ( buttonType ) {
          case 'conductor-save':
            fn.download('json', cd.data, cd.data['conductor'].conductor_name );
            break;
          case 'conductor-read':
            fn.fileSelect('json').then(function( result ){
                
            });
            break;
          case 'undo':
            cd.conductorHistory().undo();
            break;
          case 'redo':
            cd.conductorHistory().redo();
            break;
          case 'node-delete':
            cd.conductorHistory().nodeRemove( cd.select );
            cd.nodeRemove( cd.select );
            break;
          case 'view-all':
            cd.nodeViewAll( 0 );
            break;
          case 'view-reset':
            cd.canvasPositionReset();
            break;
          case 'full-screen-on':
          case 'full-screen-off':
            editor.fullScreen( $body.get(0) );
            break;
        }
        // Undo Redoは別管理
        if ( ['undo','redo'].indexOf( buttonType ) === -1 ) {
            // 一定時間ボタンを押せなくする
            $button.prop('disabled', true );

            if ( buttonType !== 'node-delete' ) {
                $button.addClass('active');
                // buttonDisabledTime ms 後に復活
                setTimeout( function(){
                    $button.removeClass('remove').prop('disabled', false );
                }, buttonDisabledTime );
            }
        }
    });
}
/*
##################################################
   infoからnameを返すeditor-edit
##################################################
*/
getName( id, type ) {
    if ( this.info.dict[ type ] && id ) {
        const name = fn.cv( this.info.dict[ type ][ id ], 'Unknown');
        return name;
    } else {
        return undefined;
    }
}
/*
##################################################
   Conductor nameを返す
##################################################
*/
getConductorName( id ) {
    return this.getName( id, 'conductor');
} 
/*
##################################################
   Movement nameを返す
##################################################
*/
getOperationName( id ) {
    return this.getName( id, 'operation');
} 
/*
##################################################
   Movement nameを返す
##################################################
*/
getMovementName( id ) {
    return this.getName( id, 'movement');
} 
/*
##################################################
   Orchestrator nameを返す
##################################################
*/
getOrchestratorName( id ) {
    return this.getName( id, 'orchestra');
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Canvas
//
////////////////////////////////////////////////////////////////////////////////////////////////////

/*
##################################################
   キャンバスの初期設定
##################################################
*/
initCanvas() {
    const cd = this;
    
    // Editor 位置とサイズ
    cd.editor = {
        canvasWidth: 16400,
        canvasHeight: 16400,
        artboradWidth: 16000,
        artboradHeight: 16000,
        scaling: 1,
        oldScaling: 1,
        area: {},
        canvas: {},
        artBoard: {},
        canvasPt: { x: 0, y: 0 },
        artBoardPt: { x: 0, y: 0 }
    };
    
    // キャンバスのスケーリング
    cd.editor.scalingNums = [
        0.025, 0.05, 0.075,
        0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
        1, 1.25, 1.5 , 1.75, 2, 2.5, 3, 4, 5, 6, 7, 8, 9
    ];
    
    // 各種サイズをセット
    cd.$.canvas.css({
        'width' : cd.editor.canvasWidth,
        'height' : cd.editor.canvasHeight
    });
    cd.$.artBoard.css({
        'width' : cd.editor.artboradWidth,
        'height' : cd.editor.artboradHeight
    });
    cd.canvasPositionReset( 0 );
    
    // --------------------------------------------------
    // ウィンドウリサイズで表示エリアのサイズを再取得
    // --------------------------------------------------
    const reiszeEndTime = 200;
    let resizeTimerID;
    cd.$.window.on('resize.editor', function(){

        clearTimeout( resizeTimerID );

        resizeTimerID = setTimeout( function(){
            cd.editor.area = cd.getSize( cd.$.area );
        }, reiszeEndTime );

    });
    
    // --------------------------------------------------
    // キャンバスの移動・拡大縮小
    // --------------------------------------------------
    cd.$.area.on({
        'mousedown.canvas': function( e ) {    
            if ( e.buttons === 2 ) {
                e.preventDefault();

                cd.setAction('canvas-move');

                const mouseDownPositionX = e.pageX,
                      mouseDownPositionY = e.pageY;

                let moveX = 0,
                    moveY = 0;

                cd.$.window.on({
                    'mousemove.canvas': function( e ){

                      moveX = e.pageX - mouseDownPositionX;
                      moveY = e.pageY - mouseDownPositionY;

                      cd.$.canvas.css({
                          'transform' : 'translate3d(' + moveX + 'px,' + moveY + 'px,0) scale(' + cd.editor.scaling + ')'
                      });
                    },
                    'contextmenu.canvas': function( e ) {
                      if ( cd.setting.debug === false ) e.preventDefault();
                      $( this ).off('contextmenu.canvas');
                    },
                    'mouseup.canvas': function(){
                      $( this ).off('mousemove.canvas mouseup.canvas');
                      cd.clearAction();

                      cd.editor.canvasPt.x = cd.editor.canvasPt.x + moveX;
                      cd.editor.canvasPt.y = cd.editor.canvasPt.y + moveY;

                      cd.$.canvas.css({
                          'left' : cd.editor.canvasPt.x,
                          'top' : cd.editor.canvasPt.y,
                          'transform' : 'translate(0,0) scale(' + cd.editor.scaling + ')'
                      });
                    }
                });
            }
        },
        'wheel.canvas': function( e ){
            e.preventDefault();
            
            const $area = $( this );

            if ( e.buttons === 0 ) {
                const mousePositionX = Math.floor( ( e.pageX - $area.offset().left - cd.editor.canvasPt.x ) / cd.editor.scaling ),
                      mousePositionY = Math.floor( ( e.pageY - $area.offset().top - cd.editor.canvasPt.y ) / cd.editor.scaling ),
                      delta = e.originalEvent.deltaY ? - ( e.originalEvent.deltaY ) : e.originalEvent.wheelDelta ? e.originalEvent.wheelDelta : - ( e.originalEvent.detail );

                if ( delta < 0 ) {
                    cd.canvasScaling('out', mousePositionX, mousePositionY );
                } else {
                    cd.canvasScaling('in', mousePositionX, mousePositionY);
                }
            }
        },
        'contextmenu': function( e ) {
            // コンテキストメニューは表示しない
            if ( cd.setting.debug === false ) e.preventDefault();
        }
    });
    
    // --------------------------------------------------
    // マウスの位置の判定
    // --------------------------------------------------
    cd.$.area.add( cd.$.panel ).on({
          'mouseenter' : function(){ $( this ).addClass('hover'); },
          'mouseleave' : function(){ $( this ).removeClass('hover'); }
    });

}
/*
##################################################
   サイズの取得
##################################################
*/
getSize( $obj ) {
    return {
        'w' : $obj.width(),
        'h' : $obj.height(),
        'l' : $obj.offset().left,
        't' : $obj.offset().top
    }
}
/*
##################################################
   指定位置にキャンバスを移動する
##################################################
*/
canvasPosition( positionX, positionY, scaling, duration ) {
    const cd = this;

    if ( duration === undefined ) duration = 0.3;

    // アニメーションさせる場合は一時的に操作できないようにする
    if ( duration !== 0 ) {
        cd.setAction('editor-pause');
        const moveX = positionX - cd.editor.canvasPt.x,
              moveY = positionY - cd.editor.canvasPt.y;
        cd.$.canvas.css({
            'transform': 'translate(' + moveX + 'px,' + moveY + 'px) scale(' + scaling + ')',
            'transition-duration': duration + 's'
        });
        setTimeout( function(){
            cd.$.canvas.css({
                'left': positionX,
                'top': positionY,
                'transform': 'translate(0,0) scale(' + scaling + ')',
                'transition-duration': '0s'
            });
            cd.clearAction();
        }, duration * 1000 );
    } else {
        cd.$.canvas.css({
            'left': positionX,
            'top': positionY,
            'transform': 'translate(0,0) scale(' + scaling + ')'
        });
    }

    if ( scaling <= 0.1 ) {
        cd.$.canvas.attr('data-scale','10');
    } else if ( scaling <= 0.25 ) {
        cd.$.canvas.attr('data-scale','25');
    } else if ( scaling <= 0.5 ) {
        cd.$.canvas.attr('data-scale','50');
    } else if ( scaling <= 0.75 ) {
        cd.$.canvas.attr('data-scale','75');
    } else {
        cd.$.canvas.removeAttr('data-scale');
    }
    
    cd.editor.canvasPt.x = positionX;
    cd.editor.canvasPt.y = positionY;
    cd.editor.scaling = scaling;
    cd.editor.oldScaling = scaling;
}
/*
##################################################
   キャンバスのポジションをリセット
##################################################
*/
canvasPositionReset( duration ) {
    const cd = this;
    
    if ( duration === undefined ) duration = 0.3;
    
    cd.editor.area = cd.getSize( cd.$.area );
    cd.editor.canvas = cd.getSize( cd.$.canvas );
    cd.editor.artBoard = cd.getSize( cd.$.artBoard );
    
    cd.editor.artBoardPt = {
      'x' : Math.round( ( cd.editor.canvas.w / 2 ) - ( cd.editor.artBoard.w / 2 ) ),
      'y' : Math.round( ( cd.editor.canvas.h / 2 ) - ( cd.editor.artBoard.h / 2 ) )
    };
    cd.$.artBoard.css({
      'left' : cd.editor.artBoardPt.x,
      'top' : cd.editor.artBoardPt.y
    });
    
    let resetX, resetY;
    if ( $('#node-1.conductor-start').length ) {
      // Start nodeがある場合は基準にする
      const $start = $('#node-1.conductor-start'),
            adjustPosition = 32; // 端Padding
      resetX = -( Number( $start.css('left').replace('px','') ) + cd.editor.artBoardPt.x - adjustPosition );
      resetY = -( Number( $start.css('top').replace('px','') ) + cd.editor.artBoardPt.y - ( ( cd.editor.area.h / 2 ) - ( $start.outerHeight() / 2 ) ) );
    } else {
      // キャンバスのセンター
      resetX = Math.round( - ( cd.editor.canvas.w / 2 ) + ( cd.editor.area.w / 2 ) );
      resetY = Math.round( - ( cd.editor.canvas.h / 2 ) + ( cd.editor.area.h / 2 ) );
    }
    cd.canvasPosition( resetX, resetY, 1, duration );
    
}
/*
##################################################
   キャンバスの拡大縮小
##################################################
*/
canvasScaling( zoomType, positionX, positionY ){
    const cd = this;
    
    const scalingNumsLength = cd.editor.scalingNums.length - 1;

    if ( positionX === undefined ) positionX = cd.editor.canvasPt.x / 2 / cd.editor.scaling;
    if ( positionY === undefined ) positionY = cd.editor.canvasPt.y / 2 / cd.editor.scaling;
    
    let scaling = cd.editor.scaling,
        scalingNum = cd.editor.scalingNums.indexOf( scaling );

    if ( zoomType === 'in') {
        if ( scalingNum === -1 ) {
            for ( let i = scalingNumsLength - 1; i >= 0; i-- ) {
                if ( scaling > cd.editor.scalingNums[ i ] ) {
                    scalingNum = i;
                    break;
                }
            }
        }
        scalingNum = ( scalingNum < scalingNumsLength ) ? scalingNum + 1 : scalingNumsLength;
        scaling = cd.editor.scalingNums[ scalingNum ];
    } else if ( zoomType === 'out') {
        if ( scalingNum === -1 ) {
            for ( let i = 0; i < scalingNumsLength; i++ ) {
                if ( scaling < cd.editor.scalingNums[ i ] ) {
                    scalingNum = i;
                    break;
                }
            }
        }
        scalingNum = ( scalingNum > 1 ) ? scalingNum - 1 : 0;
        scaling = cd.editor.scalingNums[ scalingNum ];
    } else if ( typeof zoomType === 'number') {
        scaling = zoomType;
    }

    if ( scaling !== cd.editor.oldScaling ) {
      const commonX = ( ( cd.editor.canvas.w * scaling ) - ( cd.editor.canvas.w * cd.editor.oldScaling ) ) / 2,
            commonY = ( ( cd.editor.canvas.h * scaling ) - ( cd.editor.canvas.h * cd.editor.oldScaling ) ) / 2,
            adjustX = ( ( cd.editor.canvas.w / 2 ) - positionX ) * Math.abs( scaling - cd.editor.oldScaling ),
            adjustY = ( ( cd.editor.canvas.h / 2 ) - positionY ) * Math.abs( scaling - cd.editor.oldScaling );
      
      if ( zoomType === 'in') {
          positionX= Math.round( cd.editor.canvasPt.x - commonX + adjustX );
          positionY = Math.round( cd.editor.canvasPt.y - commonY + adjustY );
      } else if ( zoomType === 'out') {
          positionX = Math.round( cd.editor.canvasPt.x - commonX - adjustX );
          positionY = Math.round( cd.editor.canvasPt.y - commonY - adjustY );
      }
      cd.canvasPosition( positionX, positionY, scaling, 0 );
    }
}
/*
##################################################
   全てのノードを表示する
##################################################
*/
nodeViewAll( duration ) {
    const cd = this;

    const canvasWidth = cd.$.area.width(),
          canvasHeight = cd.$.area.height();

    // 端の座標を求める
    let x1, y1, x2, y2;
    for ( let key in cd.data ) {
        if ( RegExp('^node-').test( key ) ) {
            let nodeX1 = Number( cd.data[ key ].x ),
                nodeY1 = Number( cd.data[ key ].y ),
                nodeX2 = Number( cd.data[ key ].x ) + Number( cd.data[ key ].w ),
                nodeY2 = Number( cd.data[ key ].y ) + Number( cd.data[ key ].h );

            // Note分調整
            const note = cd.data[ key ].note;
            if ( !note ) {
                const $note = $('#' + key ).find('.node-note'),
                      notePosition = 16,
                      noteWidth = $note.outerWidth(),
                      noteHeight = $note.outerHeight();
                if ( noteWidth > Number( cd.data[ key ].w ) ) {
                    const noteXNum = ( noteWidth - Number( cd.data[ key ].w ) ) / 2;
                    nodeX1 = nodeX1 - noteXNum;
                    nodeX2 = nodeX2 + noteXNum;
                }
                nodeY1 = nodeY1 - noteHeight - notePosition;
            }
            // 左上座標
            if ( x1 > nodeX1 || x1 === undefined ) x1 = nodeX1;
            if ( y1 > nodeY1 || y1 === undefined ) y1 = nodeY1;
            // 右下座標
            if ( x2 < nodeX2 || x2 === undefined ) x2 = nodeX2;
            if ( y2 < nodeY2 || y2 === undefined ) y2 = nodeY2;
        }
    }

    // センター座標と表示倍率
    const adjustPosition = 32, // 端Padding
          viewWidth = x2 - x1 + ( adjustPosition * 2 ),
          viewHeight = y2 - y1 + ( adjustPosition * 2 ),
          centerX = x1 + ( ( x2 - x1 ) / 2 ),
          centerY = y1 + ( ( y2 - y1 ) / 2 ),
          scalingVertical = Math.floor( canvasWidth / viewWidth * 1000 ) / 1000,
          scalingHorizontal = Math.floor( canvasHeight / viewHeight * 1000 ) / 1000,
          scaling = ( scalingVertical < scalingHorizontal ) ? scalingVertical : scalingHorizontal;

    // 全体を表示する
    cd.canvasPosition(
        Math.floor( ( -centerX - cd.editor.artBoardPt.x ) * scaling ) + ( cd.$.area.width() / 2 ),
        Math.floor( ( -centerY - cd.editor.artBoardPt.y ) * scaling ) + ( cd.$.area.height() / 2 ),
        scaling, duration
    );

    // 確認用
    if ( cd.setting.debug === true ) {
        window.console.group('View all');
        window.console.log('x1 : ' + x1 + ' , y1 : ' + y1 + ' , x2 : ' + x2 + ' , y2 : ' + y2 );
        window.console.log('View Width : ' + viewWidth + ' , View Height : ' + viewHeight );
        window.console.log('Center X : ' + centerX + ' , Center Y : ' + centerY );
        window.console.log('Vertical Scaling : ' + scalingVertical + ' , Horizontal Scaling : ' + scalingHorizontal );
        window.console.groupEnd('View all');
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   SVG area
//
////////////////////////////////////////////////////////////////////////////////////////////////////

/*
##################################################
   SVGエリアの初期設定
##################################################
*/
initSvgArea() {
    const cd = this;
    
    cd.svg = {};
    cd.svg.xmlns = 'http://www.w3.org/2000/svg';
    
    cd.$.svgArea = $( document.createElementNS( cd.svg.xmlns, 'svg') );
    cd.$.selectArea = $( document.createElementNS( cd.svg.xmlns, 'svg') );
    cd.$.selectBox = $( document.createElementNS( cd.svg.xmlns, 'rect') );
    
    cd.setSvgArea();
    
    // --------------------------------------------------
    // 線をクリックで削除する（Editモードのみ）
    // --------------------------------------------------
    cd.$.artBoard.on({
        'click' : function(){
            if ( !cd.checkAction('editor-pause') && ( cd.mode === 'edit' || cd.mode === 'update')  ) {
                const edgeID = $( this ).closest('.svg-group').attr('id');
                cd.conductorHistory().edgeRemove( edgeID );
                cd.removeEdge( edgeID );
                cd.updateConductorData();
            }
        } 
    }, '.svg-select-line');
    
    // --------------------------------------------------
    // Editモードのみホバーでクラス付与
    // --------------------------------------------------
    cd.$.area.on({
      'mouseenter' : function(){
            if ( cd.mode === 'edit' || cd.mode === 'update') {
                const $edge = $( this );
                if ( !cd.checkAction('node-move') || $edge.attr('data-interrupt') === 'true' ) {
                    $edge.attr('class','svg-group hover');
                }
                if ( $edge.attr('data-interrupt') === 'true' ) {
                    cd.$.editor.find('.node.current').css('opacity', .5 );
                }
            }
        },
        'mouseleave' : function(){
            if ( cd.mode === 'edit' || cd.mode === 'update') {
              $( this ).attr('class','svg-group');
              cd.$.editor.find('.node.current').css('opacity', 'inherit');
            }
        }
    },'.svg-group');
}
/*
##################################################
   Edge ID
##################################################
*/
edgeCounter() {
    return this.count.edge++;
}
/*
##################################################
   SVGエリアをセット
##################################################
*/
setSvgArea() {
    const cd = this;
  
    cd.$.svgArea.get(0).setAttribute('viewBox', '0 0 ' + cd.editor.artBoard.w + ' ' + cd.editor.artBoard.h );
    cd.$.selectArea.get(0).setAttribute('viewBox', '0 0 ' + cd.editor.artBoard.w + ' ' + cd.editor.artBoard.h );

    cd.$.artBoard.prepend( cd.$.svgArea, cd.$.selectArea.append( cd.$.selectBox ) );
    cd.$.svgArea.attr({
        'id' : 'svg-area',
        'width' : cd.editor.artBoard.w,
        'height' : cd.editor.artBoard.h
    });
    cd.$.selectArea.attr({
        'id' : 'select-area',
        'width' : cd.editor.artBoard.w,
        'height' : cd.editor.artBoard.h
    });

}
/*
##################################################
   線の削除
##################################################
*/
removeEdge( edgeID, removeSpeed ) {
    const cd = this;

    if ( removeSpeed === undefined ) removeSpeed = 200;

    const $edge = $('#' + edgeID ),
          edge = cd.data[ edgeID ];

    // 結線情報を削除
    if ('inTerminal' in edge ) {
        $('#' + edge.inTerminal ).removeClass('connected connect-a');
        delete cd.data[ edge.inNode ].terminal[ edge.inTerminal ].edge;
        delete cd.data[ edge.inNode ].terminal[ edge.inTerminal ].targetNode;
    }
    
    if ('outTerminal' in edge ) {
      $('#' + edge.outTerminal ).removeClass('connected connect-a');
      delete cd.data[ edge.outNode ].terminal[ edge.outTerminal ].edge;
      delete cd.data[ edge.outNode ].terminal[ edge.outTerminal ].targetNode;
    }
    delete cd.data[ edgeID ];

    if ( cd.setting.debug === true ) {
        window.console.log( 'REMOVE EDGE ID : ' + edgeID );
    }

    cd.setAction('editor-pause');
    
    $edge.animate({'opacity' : 0 }, removeSpeed, function(){
        $( this ).remove();
        cd.clearAction();
    });
}
/*
##################################################
   線（Edge,Line）作成
##################################################
*/
newSVG( svgID ) {
    const cd = this;
    
    // SVG ID
    if ( svgID === undefined ) svgID = 'line-' + cd.edgeCounter();

    // グループを作成
    const $svgGroup = $( document.createElementNS( cd.svg.xmlns, 'g') );
    $svgGroup.attr({
      'id' : svgID,
      'class' : 'svg-group'
    });

    // パスを作成
    const $svgLine = $( document.createElementNS( cd.svg.xmlns, 'path') ),
          $svgLineInside = $( document.createElementNS( cd.svg.xmlns, 'path') ),
          $svgLineOutside = $( document.createElementNS( cd.svg.xmlns, 'path') ),
          $svgLineBack = $( document.createElementNS( cd.svg.xmlns, 'path') ),
          $svgSelectLine = $( document.createElementNS( cd.svg.xmlns, 'path') );
    $svgLine.attr('class', 'svg-line');
    $svgLineInside.attr('class', 'svg-line-inside');
    $svgLineOutside.attr('class', 'svg-line-outside');
    $svgLineBack.attr('class', 'svg-line-back');
    $svgSelectLine.attr('class', 'svg-select-line');

    // SVGエリアに追加
    cd.$.svgArea.append( $svgGroup.append( $svgLineBack, $svgLineOutside, $svgLineInside, $svgLine, $svgSelectLine ) );
      
    return $svgGroup;
}
/*
##################################################
   線（Edge,Line）作成
##################################################
*/
edgeUpdate( edgeID ) {
    const cd = this;
    
    const inNodeID = cd.data[ edgeID ].inNode,
          outNodeID = cd.data[ edgeID ].outNode;
                
    const inTerminal = cd.data[ inNodeID ].terminal[ cd.data[ edgeID ].inTerminal ],
          outTerminal = cd.data[ outNodeID ].terminal[ cd.data[ edgeID ].outTerminal ];
                
    const inX = Number( inTerminal.x ),
          inY = Number( inTerminal.y ),
          outX = Number( outTerminal.x ),
          outY = Number( outTerminal.y );
                      
    $('#' + edgeID ).find('path').attr('d', cd.svgDrawPosition( outX, outY, inX, inY ) );
}
/*
##################################################
   結線済みの線の更新
##################################################
*/
connectEdgeUpdate( nodeID ) {
    const cd = this;
    
    $('#' + nodeID ).find('.connected').each( function() {
      const terminalID = $( this ).attr('id');
      if ( 'edge' in cd.data[ nodeID ].terminal[ terminalID ] ) {
        const edgeID = cd.data[ nodeID ].terminal[ terminalID ].edge;
        cd.edgeUpdate( edgeID );
      }
    });
}
/*
##################################################
   SVG命令文
##################################################
*/
svgOrder( order, position ) {
    let pathData = [];
    for( let i = 0; i < position.length; i++ ){
        pathData.push( position[ i ].join(',') );
    }
    return order + pathData.join(' ');
}
/*
##################################################
   SVG座標
##################################################
*/
svgDrawPosition( startX, startY, endX, endY ) {
    const cd = this;

    let drawPositionArray = [];
    
    // 中間点
    const centerX = Math.round( ( startX + endX ) / 2 ),
          centerY = Math.round( ( startY + endY ) / 2 );
            
    // 対象との距離
    const xRange = startX - endX,
          yRange = startY - endY;
    
    // 対象との絶対距離
    const xAbsoluteRange = Math.abs( xRange ),
          yAbsoluteRange = Math.abs( yRange );
    
    // Terminalからの直線距離
    let terminalStraightLineRange = 8;
    
    // 直線距離X座標
    const startStraightLineX = startX + terminalStraightLineRange,
          endStraightLineX = endX - terminalStraightLineRange;
    
    // SVG命令（共通）
    const moveStart = cd.svgOrder('M', [[ startX, startY]] ),
          startLine = cd.svgOrder('L', [[ startStraightLineX, startY]] ),
          moveEnd = cd.svgOrder('L', [[ endX, endY]] );          
    
    if ( yAbsoluteRange > 32 && xRange > -96 ) {
      // Back Line
      let curvetoRangeX = Math.round( xAbsoluteRange / 3 ),
          curvetoStartY1 = Math.round( startY - yRange / 20 ),
          curvetoEndY1 = Math.round( endY + yRange / 20 ),
          curvetoStartY2 = Math.round( startY - yRange / 3 );
          
      if ( curvetoRangeX < 32 ) curvetoRangeX = 32;
      if ( curvetoRangeX > 128 ) curvetoRangeX = 128;
      if ( yAbsoluteRange < 128 && xRange > 0 ) {
        let adjustY = ( yRange > 0 ) ? yRange - 128: yRange + 128;
        curvetoStartY2 = curvetoStartY2 + Math.round( adjustY / 3 );
      }
      
      if ( xAbsoluteRange > 256 && yAbsoluteRange < 256 ) {
      // Straight S Line
      const curvetoStart = cd.svgOrder('C', [[ startStraightLineX + 96, startY],[ startStraightLineX + 96, centerY ],[ startStraightLineX, centerY ]] ),
            centerLine = cd.svgOrder('L',[[ endStraightLineX, centerY ]]),
            curvetoEnd = cd.svgOrder('C', [[ endStraightLineX - 96, centerY ],[ endStraightLineX - 96, endY ],[ endStraightLineX, endY ]]);
      
      drawPositionArray = [ moveStart, startLine, curvetoStart, centerLine, curvetoEnd, moveEnd ];
      
      } else {
      // S Line
      const curvetoStartX = startStraightLineX + curvetoRangeX,
            curvetoStart = cd.svgOrder('C', [[ curvetoStartX, curvetoStartY1],[ curvetoStartX, curvetoStartY2 ],[ centerX, centerY ]] ),
            curvetoEnd = cd.svgOrder('S', [[ endStraightLineX - curvetoRangeX, curvetoEndY1 ],[ endStraightLineX, endY ]]);
      
      drawPositionArray = [ moveStart, startLine, curvetoStart, curvetoEnd, moveEnd ];
      }
      
    } else {
    
      if ( xRange > 0 ) {
        
        let curvetoRangeX = Math.round( xAbsoluteRange / 3 );
        if ( curvetoRangeX < 32 ) curvetoRangeX = 32;
        if ( curvetoRangeX > 128 ) curvetoRangeX = 128;
        // C Line
        const centerAdjust = Math.round( curvetoRangeX / 3 * 2 ),
              curvetoStartX = startStraightLineX + curvetoRangeX,
              curvetoStart = cd.svgOrder('C', [[ curvetoStartX, startY],[ curvetoStartX, startY + centerAdjust ],[ centerX, centerY + centerAdjust ]] ),
              curvetoEnd = cd.svgOrder('S', [[ endStraightLineX - curvetoRangeX, endY ],[ endStraightLineX, endY ]]);
                    
        drawPositionArray = [ moveStart, startLine, curvetoStart, curvetoEnd, moveEnd ];
      
      } else {

        let curvetoQX = startStraightLineX + Math.round( yAbsoluteRange / 3 );
        if ( curvetoQX > centerX ) curvetoQX = centerX;

        const curvetoQ = cd.svgOrder('Q', [[ curvetoQX, startY]] ),
              endLine = cd.svgOrder('T', [[ endStraightLineX, endY]] );

        drawPositionArray = [ moveStart, startLine, curvetoQ, centerX + ',' + centerY, endLine, moveEnd ];
      }
    }

    return drawPositionArray.join(' ');
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ノード
//
////////////////////////////////////////////////////////////////////////////////////////////////////

/*
##################################################
  ノード全般初期設定
##################################################
*/
initNode() {
    const cd = this;
    
    // 選択中のNode ID
    cd.select = [];
    
    // ノード追加フラグ
    cd.flag = {};
    cd.flag.nodeAdd = false;
    
    // Conductorステータス
    cd.status.conductor = cd.info.list.conductor_status;

    // Nodeステータス
    cd.status.node = cd.info.list.node_status;
    
    // Movementステータス
    cd.status.movement = {
      '6': ['fail', '異常終了'], // 異常終了
      '7': ['stop', '緊急停止'], // 緊急停止
      '9': ['done', '正常終了'], // 正常終了
      '10': ['error', '準備エラー'], // 準備エラー
      '11': ['error', '想定外エラー'], // 想定外エラー
      '14': ['skip', 'Skip完了'], // Skip完了
      '15': ['warning', '警告終了'], // 警告終了
      '9999': ['other', 'Other'],
    };

    // マージテータス
    cd.status.merge = {
      '0': ['standby'],
      '1': ['waiting'],
      '2': ['complete'],
      '3': ['unused']
    };

    // ポーズステータス
    cd.status.pause = {
      '0': ['standby','PAUSE'],
      '1': ['pause','PAUSE'],
      '2': ['resume','RESUME'],
    };    

    // 接続禁止パターン（ out Type : [in Types] ）
    cd.setting.connectablePattern = {
        'start' : ['conditional-branch','merge','pause','status-file-branch'],
        'conditional-branch' : ['conditional-branch','merge','status-file-branch'],
        'parallel-branch' : ['conditional-branch','parallel-branch','pause','status-file-branch'],
        'status-file-branch': ['conditional-branch','pause','status-file-branch','merge'],
        'merge' : ['conditional-branch','merge','status-file-branch'],
        'pause' : ['pause','end','status-file-branch'],
        'call' : ['status-file-branch']
    };
    
    // ノードテキスト
    cd.setting.nodeText = {
        'start' : ['S', 'Conductor', 'Start', 'conductor-start'],
        'end' : ['E', 'Conductor', 'End', 'conductor-end'],
        'pause' : ['', '', 'Pause', 'function function-pause'],
        'call' : ['Cc', 'Conductor call', 'Not selected', 'conductor-call'],
        'conditional-branch' : ['', '', '', 'function function-conditional'],
        'parallel-branch' : ['', '', '', 'function function-parallel'],
        'status-file-branch' : ['', '', '', 'function function-status-file'],
        'merge' : ['', '', '', 'function function-merge']
    };
        
    // --------------------------------------------------
    // リストからノード追加（ドラッグアンドドロップ）
    // --------------------------------------------------
    cd.$.panel.find('.node-table').on('mousedown', 'tbody tr', function( e ){

        if ( e.button === 0 && cd.flag.nodeAdd === false && ( cd.mode === 'edit' || cd.mode === 'update') ) {

            // 選択を解除する
            getSelection().removeAllRanges();
            cd.flag.nodeAdd = true;

            // 選択したNodeからデータを取得
            const $nodeData = $( this ).find('.add-node');

            let addNodeType, addMovementID = '';

            if ( $nodeData.is('.function') ) {
                addNodeType = $nodeData.attr('data-function-type');
            } else {
                addNodeType = 'movement';
                addMovementID = $nodeData.attr('data-id');
            }

            // 分岐ノード一覧
            const branchNode = [
                'conditional-branch',
                'parallel-branch',
                'status-file-branch',
                'merge',
            ]; 

            // モード変更
            cd.setAction('node-move');

            const $node = cd.initialNode( addNodeType, addMovementID ),
                  nodeID = $node.attr('id'),
                  mouseDownPositionX = e.pageX,
                  mouseDownPositionY = e.pageY;
            
            $node.hide();
            cd.$.editor.append( $node );

            // 要素の追加を待つ
            $node.ready(function() {

                let nodeDragTop = $node.height() / 2,
                    nodeDragLeft = 72;

                $node.addClass('drag current').css({
                    'left' : Math.round( e.pageX - cd.$.window.scrollLeft() - nodeDragLeft ),
                    'top' : Math.round( e.pageY - cd.$.window.scrollTop() - nodeDragTop ),
                    'transform-origin' : nodeDragLeft + 'px 50%'
                }).show();
                
                cd.nodeGemCheck( $node );  
                cd.nodeInterruptCheck( nodeID );

                // 分岐ノードの線を描画
                if ( branchNode.indexOf( addNodeType ) !== -1 ) {
                    cd.branchLine( nodeID, 'drop');
                }
                
                cd.$.window.on({
                    'mousemove.dragNode': function( e ){
                        const moveX = Math.round( ( e.pageX - mouseDownPositionX ) ),
                              moveY = Math.round( ( e.pageY - mouseDownPositionY ) );
                        if ( cd.$.area.is('.hover') ) {
                            $node.css('transform', 'translate3d(' + moveX + 'px,' + moveY + 'px,0) scale(' + cd.editor.scaling + ')');
                        } else {
                            $node.css('transform', 'translate3d(' + moveX + 'px,' + moveY + 'px,0) scale(1)');
                        }
                    },
                    'mouseup.dragNode': function( e ){
                        $( this ).off('mousemove.dragNode mouseup.dragNode');

                        cd.clearAction();

                        // Canvasの上にいるか
                        if ( cd.$.area.is('.hover') ) {

                          // Node を アートボードにセットする
                          nodeDragTop = nodeDragTop * cd.editor.scaling;
                          nodeDragLeft = nodeDragLeft * cd.editor.scaling;

                          const artBordPsitionX = ( cd.editor.artBoardPt.x * cd.editor.scaling ) + cd.editor.area.l + cd.editor.canvasPt.x,
                                artBordPsitionY = ( cd.editor.artBoardPt.y * cd.editor.scaling ) + cd.editor.area.t + cd.editor.canvasPt.y;
                          let nodeX = Math.round( ( e.pageX - artBordPsitionX - nodeDragLeft ) / cd.editor.scaling ),
                              nodeY = Math.round( ( e.pageY - artBordPsitionY - nodeDragTop ) / cd.editor.scaling );

                          $node.appendTo( cd.$.artBoard ).removeClass('drag current').css('opacity', 'inherit');

                          cd.nodeSet( $node, nodeX, nodeY );

                          cd.nodeDeselect();
                          cd.nodeSelect( nodeID );
                          cd.panelChange( nodeID );

                          // 線の上にいるかチェック
                          const interruptFlag = cd.nodeInterrupt( nodeID );

                          cd.conductorHistory().nodeSet( nodeID, interruptFlag );          
                          cd.updateConductorData();
                          cd.flag.nodeAdd = false;

                        } else {
                          // キャンバス外の場合は消去
                          cd.count.node -= 1;
                          delete cd.data[ nodeID ];
                          $node.animate({'opacity' : 0 }, 200, function(){
                            $( this ).remove();
                            cd.flag.nodeAdd = false;
                          });
                        }

                        cd.nodeInterruptCheckClear();
                    }
                });
            });
        }
    });
    
    // --------------------------------------------------
    // ターミナルホバー
    // --------------------------------------------------
    cd.$.area.on({
        'mouseenter' : function(){ $( this ).addClass('hover'); },
        'mouseleave' : function(){ $( this ).removeClass('hover'); }
    },'.node-terminal');
    
    // --------------------------------------------------
    // キャンバスマウスダウン処理（ノードの移動、結線、複数選択）
    // --------------------------------------------------
    cd.$.area.on('mousedown', function( e ){
        if ( e.buttons === 1 ) {
            // Viewモードは何もしない
            if ( cd.mode === 'view') return false;
            
            // Skipチェックボックス
            if ( $( e.target ).closest('.node-skip').length && cd.mode !== 'checking') {
                cd.nodeDeselect();
                const $node = $( e.target ).closest('.node'),
                      nodeID = $node.attr('id');
                cd.nodeCheckStatus( nodeID );
                cd.nodeSelect( nodeID );
                cd.panelChange( nodeID );
                return false;
            }

          // Pauseボタン
          if ( $( e.target ).is('.pause-resume-button') ) return false;

          // 選択を解除しておく
          getSelection().removeAllRanges();

          const mouseDownPositionX = e.pageX,
                mouseDownPositionY = e.pageY,
                scrollFrame = Math.floor( 1000 / 60 );

          let moveX = 0, moveY = 0,
              scrollX = 0, scrollY = 0,
              scaleMoveX = 0, scaleMoveY = 0,
              scrollDirectionX = '', scrollDirectionY = '',
              moveScrollSpeedX = 0, moveScrollSpeedY = 0,
              minScrollSpeed = 4, maxScrollSpeed = 60,
              adjustMoveSpeed = 20,
              nodeMoveScrollTimer = false,
              timerMoveFlag = false,
              moveFlag = false;

          // 位置移動
          const move = function( callback ) {
              $( window ).on({
                'mousemove.nodeMove': function( e ){

                  moveFlag = true;

                  moveX = e.pageX - mouseDownPositionX;
                  moveY = e.pageY - mouseDownPositionY;

                  let positionX = e.pageX - cd.editor.area.l,
                      positionY = e.pageY - cd.editor.area.t;

                  // キャンバス外の向き
                  // X over
                  if ( positionX < 1 ) {
                      moveScrollSpeedX = Math.round( -positionX / adjustMoveSpeed );
                      scrollDirectionX = 'left';
                  } else if ( positionX > cd.editor.area.w ) {
                      moveScrollSpeedX = Math.round( ( positionX - cd.editor.area.w ) / adjustMoveSpeed ); 
                      scrollDirectionX = 'right';
                  } else {
                      scrollDirectionX = '';
                  }
                  // Y over
                  if ( positionY < 1 ) {
                      moveScrollSpeedY = Math.round( -positionY / adjustMoveSpeed );
                      scrollDirectionY = 'top';
                  } else if ( positionY > cd.editor.area.h ) {
                      moveScrollSpeedY = Math.round( ( positionY - cd.editor.area.h ) / adjustMoveSpeed ); 
                      scrollDirectionY = 'bottom';
                  } else {
                      scrollDirectionY = '';
                  }

                  if ( timerMoveFlag === false ) {
                      callback('mousemove');
                  }
                },
                'mouseup.nodeMove': function(){
                    $( this ).off('mousemove.nodeMove mouseup.nodeMove');
                    cd.$.area.off('mouseenter.canvasScroll mouseleave.canvasScroll');

                    callback('mouseup');

                    clearInterval( nodeMoveScrollTimer );
                    cd.clearAction();
                }
              });
          };

          // キャンバススクロール
          const canvasScroll = function( callback ) {
              cd.$.area.on({
                  'mouseenter.canvasScroll' : function(){
                      timerMoveFlag = false;
                      clearInterval( nodeMoveScrollTimer );
                      nodeMoveScrollTimer = false;
                  },
                  'mouseleave.canvasScroll' : function(){
                      if ( nodeMoveScrollTimer === false ) {
                          nodeMoveScrollTimer = setInterval( function(){
                              timerMoveFlag = true;

                              if ( moveScrollSpeedX < minScrollSpeed ) moveScrollSpeedX = minScrollSpeed;
                              if ( moveScrollSpeedY < minScrollSpeed ) moveScrollSpeedY = minScrollSpeed;
                              if ( moveScrollSpeedX > maxScrollSpeed ) moveScrollSpeedX = maxScrollSpeed;
                              if ( moveScrollSpeedY > maxScrollSpeed ) moveScrollSpeedY = maxScrollSpeed;

                              // X scroll
                              if ( scrollDirectionX === 'left' ) {
                                scrollX = scrollX - moveScrollSpeedX;
                                cd.editor.canvasPt.x = cd.editor.canvasPt.x + moveScrollSpeedX;
                              } else if ( scrollDirectionX === 'right' ) {
                                scrollX = scrollX + moveScrollSpeedX;
                                cd.editor.canvasPt.x = cd.editor.canvasPt.x - moveScrollSpeedX;
                              }
                              // Y scroll
                              if ( scrollDirectionY === 'top' ) {
                                scrollY = scrollY - moveScrollSpeedY;
                                cd.editor.canvasPt.y = cd.editor.canvasPt.y + moveScrollSpeedY;
                              } else if ( scrollDirectionY === 'bottom' ) {
                                scrollY = scrollY + moveScrollSpeedY;
                                cd.editor.canvasPt.y = cd.editor.canvasPt.y - moveScrollSpeedY;
                              }

                              cd.$.canvas.css({
                                  'left' : cd.editor.canvasPt.x,
                                  'top' : cd.editor.canvasPt.y
                              });

                              callback('mousemove');

                          }, scrollFrame );
                      }
                  }
              });
          };

          // 移動座標をセット
          const scaleMoveSet = function() {
              scaleMoveX = Math.round( ( moveX + scrollX ) / cd.editor.scaling );
              scaleMoveY = Math.round( ( moveY + scrollY ) / cd.editor.scaling );
          };

          // ノードの上でマウスダウン
          if ( $( e.target ).closest('.node').length ) {

            // Node移動、新規Edge 共通処理
            e.stopPropagation();

            const $node = $( e.target ).closest('.node'),
                  nodeID = $node.attr('id');

            // マウスダウンした場所がTerminalなら新規Edge作成
            if ( $node.find('.node-terminal').is('.hover') && ( cd.mode === 'edit' || cd.mode === 'update') ) {

              const $terminal = $node.find('.node-terminal.hover'),
                    terminalID = $terminal.attr('id'),
                    $edge = cd.newSVG(),
                    edgeID = $edge.attr('id'),
                    $path = $edge.find('path');

              // 接続済みなら何もしない
              if ( $terminal.is('.connected') ) return false;

              $node.addClass('current');
              $terminal.addClass('connect connect-a');

              let connectMode,
                  start_p = {
                    'x': Number( cd.data[ nodeID ].terminal[ terminalID ].x ),
                    'y' : Number( cd.data[ nodeID ].terminal[ terminalID ].y )
                  };

              if ( $terminal.is('.node-in') ) {
                connectMode = 'in-out';
              } else {
                connectMode = 'out-in';
              }

              cd.setAction('edge-connect');

              // 接続可能な対象を調査
              cd.edgeConnectCheck( nodeID, connectMode );

              const drawLine = function( event ) {

                scaleMoveSet();
                let end_p = {
                    'x' : start_p.x + scaleMoveX,
                    'y' : start_p.y + scaleMoveY
                }

                // 接続可能なターミナルの上かチェック
                const $targetTerminal = $('.node-terminal.wait-connect.hover');
                if ( $targetTerminal.length ) {

                  cd.nodeDeselect();
                  cd.panelChange();

                  const targetTerminalID = $targetTerminal.attr('id'),
                        $targetNode = $targetTerminal.closest('.node'),
                        targetNodeID = $targetNode.attr('id');              

                  // 中心にスナップ
                  end_p.x = Number( cd.data[ targetNodeID ].terminal[ targetTerminalID ].x );
                  end_p.y = Number( cd.data[ targetNodeID ].terminal[ targetTerminalID ].y );

                  // コネクト処理
                  if ( event === 'mouseup' ) {
                    $node.removeClass('current');
                    $terminal.removeClass('connect');
                    cd.$.artBoard.find('.forbidden').removeClass('forbidden');

                    // 接続状態を紐づけする
                    if ( connectMode === 'out-in') {
                      cd.nodeConnect( edgeID, nodeID, terminalID, targetNodeID, targetTerminalID );
                    }  else if ( connectMode === 'in-out') {
                      cd.nodeConnect( edgeID, targetNodeID, targetTerminalID, nodeID, terminalID );
                    }
                    $('#' + targetTerminalID ).addClass('connect-a');

                    // ループするか条件分岐がマージしていないかチェックする
                    if (
                      ( connectMode === 'out-in' && !cd.nodeLoopCheck( nodeID ) ) ||
                      ( connectMode === 'in-out' && !cd.nodeLoopCheck( targetNodeID) ) ||
                      ( !cd.nodeConditionalToMergeCheck() )
                    ) {
                      cd.removeEdge( edgeID );
                    } else {
                      // 接続確定
                      cd.conductorHistory().connect( edgeID );
                      cd.updateConductorData();
                    }
                    cd.edgeConnectCheckClear();
                  }

                } else if ( event === 'mouseup' ) {
                  cd.edgeConnectCheckClear();
                  $node.removeClass('current');
                  $terminal.removeClass('connect connected connect-a');
                  cd.count.edge--;
                  $edge.animate({'opacity' : 0 }, 200, function(){
                    $( this ).remove();
                  });
                }

                // 線を更新
                if ( connectMode === 'out-in') {
                  $path.attr('d', cd.svgDrawPosition( start_p.x, start_p.y, end_p.x, end_p.y ) );
                } else if ( connectMode === 'in-out') {
                  $path.attr('d', cd.svgDrawPosition( end_p.x, end_p.y, start_p.x, start_p.y ) );
                }

              };
              move( drawLine );
              canvasScroll( drawLine );

              $path.attr('d', cd.svgDrawPosition( start_p.x, start_p.y, start_p.x, start_p.y ) );

            } else if ( cd.mode === 'edit' || cd.mode === 'update') {

              // Nodeの移動
              $node.addClass('current');

              // 選択状態かどうか
              if ( !$node.is('.selected') ) { 
                // Shiftキーが押されていれば選択を解除しない
                if ( !e.shiftKey ) {
                  cd.nodeDeselect();
                  cd.panelChange();
                }
                // ノード Selected
                cd.nodeSelect( nodeID );
              } else {
                 // 選択状態かつShiftキーが押されていれば選択を解除し終了
                if ( e.shiftKey ) {
                  cd.nodeDeselect( nodeID );
                  cd.panelChange();
                  return false;
                }
              }

              // 選択しているノードの数
              const selectNodeLength = cd.select.length;

              // 選択しているノードから移動する線をリスト化する
              const selectNodeMoveLineArray = [];
              for ( let i = 0; i < selectNodeLength; i++ ) {
                const selectNodeID = cd.select[ i ];
                // ターミナル数ループ
                for ( let terminalID in cd.data[ selectNodeID ].terminal ) {
                  const terminal = cd.data[ selectNodeID ].terminal[ terminalID ];
                  if ( 'edge' in terminal ) {
                    const edgeID = cd.data[ terminal.edge ].id;
                    if ( selectNodeMoveLineArray.indexOf( edgeID ) === -1 ) {
                      selectNodeMoveLineArray.push( edgeID );
                    }
                  }
                }            
              }
              const selectNodeLineLength = selectNodeMoveLineArray.length;

              cd.setAction('node-move');
              cd.nodeInterruptCheck( nodeID );

              // パネル変更
              cd.panelChange( nodeID );

              // ノード移動処理
              const moveNode = function( event ){

                if ( event === 'mousemove') {

                  scaleMoveSet();

                  // 選択ノードをすべて仮移動
                  cd.$.area.find('.node.selected')
                    .css('transform', 'translate3d(' + scaleMoveX + 'px,' + scaleMoveY + 'px,0)');

                  // 選択ノードに接続している線をすべて移動
                  for ( let i = 0; i < selectNodeLineLength; i++ ) {
                    const moveLineID = selectNodeMoveLineArray[ i ],
                          inNodeID = cd.data[ moveLineID ].inNode,
                          outNodeID = cd.data[ moveLineID ].outNode;

                    const inTerminal = cd.data[ inNodeID ].terminal[ cd.data[ moveLineID ].inTerminal ],
                          outTerminal = cd.data[ outNodeID ].terminal[ cd.data[ moveLineID ].outTerminal ];

                    let inX = Number( inTerminal.x ),
                        inY = Number( inTerminal.y ),
                        outX = Number( outTerminal.x ),
                        outY = Number( outTerminal.y );

                    // 選択中のノードなら移動させる
                    if ( cd.select.indexOf( inNodeID ) !== -1 ) {
                        inX += scaleMoveX;
                        inY += scaleMoveY;
                    }
                    if ( cd.select.indexOf( outNodeID ) !== -1 ) {
                        outX += scaleMoveX;
                        outY += scaleMoveY;
                    }

                    $('#' + selectNodeMoveLineArray[ i ] ).find('path')
                      .attr('d', cd.svgDrawPosition( outX, outY, inX, inY ) );
                  }

                } else if ( event === 'mouseup') {
                  $node.removeClass('current').css('opacity', 'inherit');

                  // 移動しているか？
                  if ( moveFlag === true ) {
                    // 選択ノード全ての位置確定
                    const nodeSetFunc = function( setNodeID ) {
                      const beforeX = Number( cd.data[ setNodeID ].x ),
                            beforeY = Number( cd.data[ setNodeID ].y );
                      cd.nodeSet( $('#' + setNodeID ), scaleMoveX + beforeX, scaleMoveY + beforeY );
                    }
                    for ( let i = 0; i < selectNodeLength; i++ ) {
                      nodeSetFunc( cd.select[ i ] );
                    }

                    // 割り込み判定
                    const interruptFlag = cd.nodeInterrupt( nodeID );

                    cd.conductorHistory().move( cd.select, scaleMoveX, scaleMoveY, interruptFlag );
                    cd.updateConductorData();
                  }

                  cd.nodeInterruptCheckClear();
                }

              };

              move( moveNode );
              canvasScroll( moveNode );

            } else {
              // Editモード以外は選択するのみ
              if ( !$node.is('.selected') ) { 
                cd.nodeDeselect();
                cd.nodeSelect( nodeID );
                cd.panelChange( nodeID );
              }
            }


          // 線の上
          } else if ( $( e.target ).is('.svg-select-line') ) {

            cd.nodeDeselect();
            cd.panelChange();

          // その他
          } else {

            // 全ての選択を解除
            if ( !e.shiftKey ) cd.nodeDeselect();
            cd.panelChange();

            // Editモードなら範囲選択
            if ( cd.mode === 'edit' || cd.mode === 'update') {

              cd.setAction('node-select');

              const positionNow = {
                'x' : function ( x ) {
                  x = Math.round( ( x - ( cd.editor.artBoardPt.x * cd.editor.scaling ) - cd.editor.area.l - cd.editor.canvasPt.x ) / cd.editor.scaling );
                  return x;
                },
                'y' : function ( y ) {
                  y = Math.round( ( y - ( cd.editor.artBoardPt.y * cd.editor.scaling ) - cd.editor.area.t - cd.editor.canvasPt.y ) / cd.editor.scaling )
                  return y;
                }
              };
              const rectX = positionNow.x( mouseDownPositionX ) - 0.5,
                    rectY = positionNow.y( mouseDownPositionY ) - 0.5;

              let x,y,w,h;

              const rectDraw = function( event ) {

                if ( event === 'mousemove') {

                  scaleMoveSet();

                  if ( scaleMoveX < 0 ) {
                    x = rectX + scaleMoveX;
                    w = -scaleMoveX;
                  } else {
                    x = rectX;
                    w = scaleMoveX;
                  }
                  if ( scaleMoveY < 0 ) {
                    y = rectY + scaleMoveY;
                    h = -scaleMoveY;
                  } else {
                    y = rectY;
                    h = scaleMoveY;
                  }
                  cd.$.selectArea.find('rect').attr({
                    'x' : x, 'y' : y, 'width' : w, 'height' : h
                  });
                } else if ( event === 'mouseup') {
                  cd.$.selectArea.find('rect').attr({
                    'x' : 0, 'y' : 0, 'width' : 0, 'height' : 0
                  });
                  cd.clearAction();
                  // 選択範囲内のノードを選択
                  const rect = {
                    'left' : x,
                    'top' : y,
                    'right' : x + w,
                    'bottom' : y + h
                  };
                  for ( let nodeID in cd.data ) {
                    if ( 'type' in cd.data[ nodeID ] ) {
                      if ( cd.data[ nodeID ].type !== 'edge' ) {
                        const node = {
                          'left' : Number( cd.data[ nodeID ].x ),
                          'top' : Number( cd.data[ nodeID ].y ),
                          'right' : Number( cd.data[ nodeID ].x ) + Number( cd.data[ nodeID ].w ),
                          'bottom' : Number( cd.data[ nodeID ].y ) + Number( cd.data[ nodeID ].h )
                        };
                        // 判定
                        if ( ( node.top < rect.bottom && rect.top < node.bottom ) &&
                             ( node.left < rect.right && rect.left < node.right ) ) {
                          // 選択状態を反転
                          if ( cd.select.indexOf( nodeID ) === -1 ) {
                            cd.nodeSelect( nodeID );
                          } else {
                            cd.nodeDeselect( nodeID );
                          }
                          if ( cd.select.length === 1 ) {
                            cd.panelChange( nodeID );
                          } else {
                            cd.panelChange();
                          }
                        }
                      }
                    }
                  } 
                }
              };
              move( rectDraw );
              canvasScroll( rectDraw );
            }
          }
        }
    });
}
/*
##################################################
   Node ID
##################################################
*/
nodeCounter() {
    return this.count.node++;
}
/*
##################################################
   Terminal ID
##################################################
*/
terminalCounter() {
    return this.count.terminal++;
}
/*
##################################################
   In or Out のTerminal ID
##################################################
*/
terminalInOutID( terminals, terminalInOut ) {
  let terminalIDList = [];
  for ( let key in terminals ) {
    if ( terminals[ key ].type === terminalInOut ) {
      terminalIDList.push( key );
    }
  }
  return terminalIDList;
}
/*
##################################################
   Terminal HTML
##################################################
*/
createTerminalHTML( terminalInOut, terminalID ) {
    let terminalHTML;

    if ( terminalID !== undefined ) {
      terminalHTML = ''
        + '<div id="' + terminalID + '" class="node-terminal node-' + terminalInOut + '">'
          + '<span class="connect-mark"></span>'
          + '<span class="hole"><span class="hole-inner"></span></span>'
        + '</div>';
    } else {
      // terminalIDの指定がない場合はCap
      terminalHTML = '<div class="node-cap node-' + terminalInOut + '"></div>'
    }

    return terminalHTML;
}
/*
##################################################
   Merge status HTML
##################################################
*/
mergeStatusHTML() {
    const cd = this;
    
    const html = [];
    for ( let statusID in cd.status.merge ) {
        html.push('<li class="merge-status-item merge-status-' + cd.status.merge[ statusID ][ 0 ] +'">'
            + cd.status.merge[ statusID ][ 0 ].toUpperCase()
        + '</li>');
    }
    
    return `
    <div class="node-body">
        <div class="merge-status" data-status="standby">
            <ul class="merge-status-list">
                ${html.join('')}
            </ul>
        </div>
    </div>`;
}
/*
##################################################
   Pause status HTML
##################################################
*/
pauseStatusHTML() {
  const cd = this;
    
    const html = [];
    for ( let statusID in cd.status.pause ) {
        html.push('<li class="pause-status-item pause-status-' + cd.status.pause[ statusID ][ 0 ] +'">'
            + cd.status.pause[ statusID ][ 1 ]
        + '</li>');
    }
    
    return `
    <div class="node-body">
        <div class="pause-status" data-status="standby">
            <ul class="pause-status-list">
                ${html.join('')}
            </ul>
        </div><div class="pause-resume">
            <button title="Resume" class="pause-resume-button" tabindex="-1" disabled></button>
        </div>
    </div>`;
}
/*
##################################################
   Node作成
##################################################
*/
createNode( nodeID ) {
    const cd = this;

    const nodeData = cd.data[ nodeID ],
          nodeText = cd.setting.nodeText;

    let nodeHTML = '',
        typeCheck = [],
        nodeClass = ['node'],
        attrData = [];

    if ( nodeData.type !== 'movement') {
        nodeClass.push( nodeText[ nodeData.type ][ 3 ] );
    }

    // Merge
    if ( nodeData.type === 'merge') {
        const terminalIDList = cd.terminalInOutID( nodeData.terminal, 'in'),
              terminalLength = terminalIDList.length;
        nodeHTML += '<div class="node-merge">'
        for ( let i = 0; i < terminalLength; i++ ) {
            nodeHTML += '<div class="node-sub">' + cd.createTerminalHTML('in', terminalIDList[ i ] );

            // Merge status
            nodeHTML += cd.mergeStatusHTML();

            nodeHTML += '<div class="branch-cap branch-out"></div></div>';
        }
        nodeHTML += '</div>'
        + '<div class="branch-line"><svg></svg></div>';
    }

    // Node main
    nodeHTML += '<div class="node-main">';

    // Terminal in CAP
    typeCheck = ['start', 'merge'];
    if ( typeCheck.indexOf( nodeData.type ) !== -1 ) {
        nodeHTML += cd.createTerminalHTML('in');
    } else {
      const terminalInID = cd.terminalInOutID( nodeData.terminal, 'in');
        nodeHTML += cd.createTerminalHTML('in', terminalInID[0] );
    }

    // Node body
    nodeHTML += '<div class="node-body">';

    let nodeCircle, nodeType, nodeName;
    if ( nodeData.type === 'movement') {
        const movementData = cd.info.list.movement.find(function( m ){
            return nodeData.movement_id === m.id;
        });
        nodeCircle = 'M';
        /*
        if ( nodeData.movement_id.length > 4 ) {
            nodeCircle = nodeData.movement_id.slice( 0, 4 );
        } else {
            nodeCircle = nodeData.movement_id;
        }
        */
        
        // IDからオーケストラと名前を設定する
        if ( movementData !== undefined ) {
            cd.data[ nodeID ]['orchestra_id'] = movementData.orchestra_id;
            cd.data[ nodeID ]['movement_name'] = movementData.name;     
        } else {
            // 見つからない場合
            cd.data[ nodeID ]['orchestra_id'] = 0;
            cd.data[ nodeID ]['movement_name'] = 'Unknown';
        }
        nodeType = cd.info.dict.orchestra[ cd.data[ nodeID ]['orchestra_id'] ];
        if ( nodeType === undefined ) nodeType = 'Unknown';
        nodeName = cd.data[ nodeID ]['movement_name'];   
        nodeClass.push('node-' + nodeType.toLocaleLowerCase().replace(/\s/g, '-') );
    } else {
        nodeCircle = nodeText[ nodeData.type ][0];
        nodeType = nodeText[ nodeData.type ][1];
        nodeName = nodeText[ nodeData.type ][2];
    }
    
    if ( nodeData.type === 'end') {
        const endStatus = cd.status.end[ cd.data[ nodeID ].end_type ][1],
              endID = cd.status.end[ cd.data[ nodeID ].end_type ][0];
        if ( cd.data[ nodeID ].end_type !== '5') {
            nodeName += ' : ' + endStatus;
        }
        attrData.push('data-end-status="' + endID + '"');
    }

    // Node circle & Node type
    typeCheck = ['start', 'end', 'movement', 'call'];
    if ( typeCheck.indexOf( nodeData.type ) !== -1 ) {
        nodeHTML += ''
        + '<div class="node-circle">'
          + '<span class="node-gem"><span class="node-gem-inner node-gem-length-' + nodeCircle.length + '">' + nodeCircle + '</span></span>'
          + '<span class="node-running"></span>'
          + '<span class="node-result" data-result-text="" data-href="#"></span>'
          + '<span class="node-end-status"><span class="node-end-status-inner"></span></span>'
        + '</div>'
        + '<div class="node-type"><span>' + nodeType + '</span></div>';
    }
    // Node name
    typeCheck = ['start', 'end', 'movement'];
    if ( typeCheck.indexOf( nodeData.type ) !== -1 ) {
        nodeHTML += '<div class="node-name"><span>' + nodeName + '</span></div>';
    }
    if ( nodeData.type === 'call' ) {
        const callConductorId = nodeData['call_conductor_id'];
        if ( callConductorId !== undefined && callConductorId !== null ) {
            nodeClass.push('call-select');
            nodeName = '[' + nodeData['call_conductor_id'] + ']:' + cd.info.dict.conductor[ callConductorId ];
            if ( cd.mode === 'checking') nodeName = cd.info.dict.conductor[ callConductorId ];
        }
        nodeHTML += ``
        + `<div class="node-name">`
            + `<span class="select-conductor-name">`
                + `<span class="select-conductor-name-inner">${nodeName}</span>`
            + `</span>`
        + `</div>`;
    }
    
    // Pause
    if ( nodeData.type === 'pause' ) {
      nodeHTML += cd.pauseStatusHTML();
    }
    
    // Status file
    if ( nodeData.type === 'status-file-branch' ) {
      nodeHTML += '<div class="node-type"><span>Status file</span></div>'
        + '<div class="node-name">'
          + '<span class="status-file-result"><span class="status-file-result-inner"></span></span>'
        + '</div>';
    }
    
    // Node body END
    nodeHTML += '</div>';

    // Terminal out CAP
    typeCheck = ['end', 'parallel-branch', 'conditional-branch', 'status-file-branch'];
    if ( typeCheck.indexOf( nodeData.type ) !== -1 ) {
        nodeHTML += cd.createTerminalHTML('out');
    } else {
        const terminalOutID = cd.terminalInOutID( nodeData.terminal, 'out');
        nodeHTML += cd.createTerminalHTML('out', terminalOutID[0] );
    }

    // Node main END
    nodeHTML += '</div>';

    // Branch
    typeCheck = ['parallel-branch', 'conditional-branch', 'status-file-branch'];
    if ( typeCheck.indexOf( nodeData.type ) !== -1 ) {
      nodeHTML += '<div class="branch-line"><svg></svg></div>'
      + '<div class="node-branch">';
      const terminalIDList = cd.terminalInOutID( nodeData.terminal, 'out'),
            terminalLength = terminalIDList.length;
      let caseNumberHTML = {};
      for ( let i = 0; i < terminalLength; i++ ) {
          let conditionList = nodeData.terminal[ terminalIDList[ i ] ].condition,
              caseNumber = nodeData.terminal[ terminalIDList[ i ] ].case;

          if ( caseNumber === undefined ) caseNumber = 'undefined' + i;

          if ( conditionList !== undefined && Number( conditionList[0] ) === 9999 ) {
              caseNumberHTML[ caseNumber ] = '<div class="node-sub default">';
          } else if ( nodeData.terminal[ terminalIDList[ i ] ].case === 'else') {
              caseNumberHTML[ caseNumber ] = '<div class="node-sub default">';
          } else {
              caseNumberHTML[ caseNumber ] = '<div class="node-sub">';
          }
          caseNumberHTML[ caseNumber ] += '<div class="branch-cap branch-in"></div>';

          // ムーブメント結果条件
          if ( nodeData.type === 'conditional-branch' ) {
              const conditionLength = conditionList.length;
              caseNumberHTML[ caseNumber ] += '<div class="node-body">'
              + '<div class="branch-type"><ul>';
              for ( let j = 0; j < conditionLength; j++ ) {
                  const conditionID = conditionList[ j ];
                  let conditionClass = cd.status.movement[ conditionID ][0];
                  caseNumberHTML[ caseNumber ] += '<li class="' + conditionClass + '" data-end-status="' + conditionID + '">' + cd.status.movement[ conditionID ][1] + '</li>';
              }
              caseNumberHTML[ caseNumber ] += '</ul></div>'
              + '</div>';
          }
          // ステータスファイル分岐
          if ( nodeData.type === 'status-file-branch' ) {
              if ( conditionList === undefined ) conditionList = [''];
              caseNumberHTML[ caseNumber ] += cd.statuFileBranchBodyHTML( caseNumber, (caseNumber === 'else')? true: false, conditionList.join('') );
          }        
          caseNumberHTML[ caseNumber ] += cd.createTerminalHTML('out', terminalIDList[ i ] ) + '</div>';
      }
      
      for ( const html in caseNumberHTML ) {
        nodeHTML += caseNumberHTML[html];
      }
      nodeHTML += '</div>';
    }

    // Note
    let noteText = nodeData['note'];
    if ( noteText !== undefined && noteText !== null ) {
        noteText = fn.escape( noteText, true );
        nodeHTML += '<div class="node-note note-open"><div class="node-note-inner"><p>' + noteText + '</p></div></div>';
    } else {
        nodeHTML += '<div class="node-note"><div class="node-note-inner"><p></p></div></div>';
    }

    // Skip, Status, Operation
    typeCheck = ['movement', 'call', 'call_s'];
    if ( typeCheck.indexOf( nodeData.type ) !== -1 ) {
      // Default skip
      let nodeCheckedType = '',
          skipFlag = false;
      // 個別Operation
      let nodeOperationData = '',
          selectOperationID = '',
          selectOperationName = '';
      // 作業確認の場合はステータス情報を参照する
      if ( cd.mode === 'checking') {
          skipFlag = ( cd.status.conductor['node_info'][ nodeID ]['skip'] === '2' ) ? true : false;
          selectOperationID = cd.status.conductor['node_info'][ nodeID ]['operation_id'];
          selectOperationName = cd.status.conductor['node_info'][ nodeID ]['oepration_name'];
      } else {
          skipFlag = ( Number( nodeData.SKIP_FLAG ) === 1 ) ? true : false;
          selectOperationID = nodeData['OPERATION_NO_IDBH'];
          selectOperationName = cd.info.dict.operation[ selectOperationID ];
      }
      
      if ( skipFlag ) {
          nodeCheckedType = ' checked';
          nodeClass.push('skip');
      }
      if ( selectOperationID !== undefined && selectOperationID !== null ) {
        nodeClass.push('operation');
        nodeOperationData = '[' + selectOperationID + ']:' + selectOperationName;
        if ( cd.mode === 'checking') nodeOperationData = selectOperationName;
      }
      nodeHTML += ''
      + '<div class="node-skip"><input class="node-skip-checkbox" tabindex="-1" type="checkbox"' + nodeCheckedType + '><label class="node-skip-label">Skip</label></div>'
      + '<div class="node-operation">'
        + '<dl class="node-operation-body">'
          + '<dt class="node-operation-name">OP</dt>'
          + '<dd class="node-operation-data">' + nodeOperationData + '</dd>'
        + '</dl>'
        + '<div class="node-operation-border"></div>'
      + '</div>'
      + '<div class="node-status"><p></p></div>';
    }

    // Node wrap
    nodeHTML = '<div id="' + nodeID + '" class="' + nodeClass.join(' ') + '" ' + attrData.join(' ') + '>' + nodeHTML + '</div>';

    return $( nodeHTML );

}
/*
##################################################
   Node初期設定
##################################################
*/
initialNode( nodeType, movementID ) {
    const cd = this;
    
    const nodeID = 'node-' + cd.nodeCounter();
    
    let typeCheck;
    
    cd.data[ nodeID ] = {
        'type' : nodeType,
        'id' : nodeID,
        'terminal' : {}
    }
    
    // Start, Merge 以外
    typeCheck = ['start', 'merge'];
    if ( typeCheck.indexOf( nodeType ) === -1 ) {
      const inTerminalID = 'terminal-' + cd.terminalCounter();
      cd.data[ nodeID ]['terminal'][ inTerminalID ] = {
        'id' : inTerminalID,
        'type' : 'in'
      }
    }
    
    // Merge
    typeCheck = ['merge'];
    if ( typeCheck.indexOf( nodeType ) !== -1 ) {
      const inTerminalID1 = 'terminal-' + cd.terminalCounter(),
            inTerminalID2 = 'terminal-' + cd.terminalCounter();
      cd.data[ nodeID ]['terminal'][ inTerminalID1 ] = {
        'id' : inTerminalID1,
        'type' : 'in'
      }
      cd.data[ nodeID ]['terminal'][ inTerminalID2 ] = {
        'id' : inTerminalID2,
        'type' : 'in'
      }
    }
    
    // Branch
    typeCheck = ['parallel-branch', 'conditional-branch', 'status-file-branch'];
    if ( typeCheck.indexOf( nodeType ) !== -1 ) {
      const outTerminalID1 = 'terminal-' + cd.terminalCounter(),
            outTerminalID2 = 'terminal-' + cd.terminalCounter();
      cd.data[ nodeID ]['terminal'][ outTerminalID1 ] = {
        'id' : outTerminalID1,
        'type' : 'out'
      }
      cd.data[ nodeID ]['terminal'][ outTerminalID2 ] = {
        'id' : outTerminalID2,
        'type' : 'out'
      }
      if ( nodeType === 'conditional-branch') {
        cd.data[ nodeID ]['terminal'][ outTerminalID1 ]['condition'] = [ 9 ];
        cd.data[ nodeID ]['terminal'][ outTerminalID2 ]['condition'] = [ 9999 ];
      } else if ( nodeType === 'status-file-branch') {
        cd.data[ nodeID ]['terminal'][ outTerminalID1 ]['case'] = 1;
        cd.data[ nodeID ]['terminal'][ outTerminalID2 ]['case'] = 'else';
      }
    }
      
    typeCheck = ['end', 'parallel-branch', 'conditional-branch', 'status-file-branch'];
    if ( typeCheck.indexOf( nodeType ) === -1 ) {
      const outTerminalID = 'terminal-' + cd.terminalCounter();
      cd.data[ nodeID ]['terminal'][ outTerminalID ] = {
        'id' : outTerminalID,
        'type' : 'out'
      }
    }
    
    if ( nodeType === 'movement' && movementID !== undefined ) {
      cd.data[ nodeID ]['movement_id'] = movementID;
      cd.data[ nodeID ]['skip_flag'] = 0;
      cd.data[ nodeID ]['operation_id'] = null;      
    }
    
    if ( nodeType === 'call' ) {
      cd.data[ nodeID ]['skip_flag'] = 0;
      cd.data[ nodeID ]['call_conductor_id'] = null;
      cd.data[ nodeID ]['operation_id'] = null;
    }
    
    if ( nodeType === 'end' ) {
      cd.data[ nodeID ]['end_type'] = '5';
    }

    return cd.createNode( nodeID );
    
}
/*
##################################################
   分岐線追加・更新
##################################################
*/
branchLine( nodeID, setMode ) {
  const cd = this;
  
  const branchType = cd.data[ nodeID ].type;

  const $branchNode = $('#' + nodeID ),
        $branchSVG = $branchNode.find('svg');
  
  // 一旦リセット
  $branchSVG.css('height', 8 ).attr('height', 8 ).empty();
  
  // サイズ決定
  const width = 40,
        height = $branchNode.height() + 2;
        
  $branchSVG.attr({
    'width' : width,
    'height' : height
  }).css({
    'width' : width,
    'height' : height
  }).get(0)
  .setAttribute('viewBox', '0 0 ' + width + ' ' + height );
  
  const terminalHeight = $branchNode.find('.node-main').height() - 16,
        terminalPosition = ( height - terminalHeight ) / 2,
        lineInterval = $branchNode.find('.node-sub').length + 1;

  $branchNode.find('.node-sub').each( function( index ){
  
    const $subNode = $( this ).find('.node-terminal'),
          terminalID = $subNode.attr('id'),
          $branchLine = $( document.createElementNS( cd.svg.xmlns, 'path') ),
          $branchInLine = $( document.createElementNS( cd.svg.xmlns, 'path') ),
          $branchOutLine = $( document.createElementNS( cd.svg.xmlns, 'path') ),
          $branchBackLine = $( document.createElementNS( cd.svg.xmlns, 'path') ),
          endY = terminalPosition + ( terminalHeight / lineInterval * ( index + 1 ) );
    
    let startY;
    if ( setMode === 'drop' ) {
      startY = $subNode.position().top + ( $subNode.height() / 2 ) + 1;
    } else {
      startY = Math.round( $subNode.position().top / cd.editor.scaling ) + ( $subNode.height() / 2 ) + 1;
    }
    
    let order;
    
    // 追加
    $branchSVG.prepend( $branchBackLine );
    $branchSVG.append( $branchOutLine, $branchInLine, $branchLine );
    // class
    const terminalClass = terminalID + '-branch-line';
    $branchLine.attr('class','branch-line ' + terminalClass );
    $branchInLine.attr('class','branch-in-line ' + terminalClass );
    $branchOutLine.attr('class','branch-out-line ' + terminalClass );
    $branchBackLine.attr('class','branch-back-line ' + terminalClass );
    // 座標設定
    if ( branchType === 'merge' ) {
      order = cd.svgOrder('M',[[0,startY]]) + cd.svgOrder('C',[[30,startY],[width-30,endY],[width,endY]]);
    } else {
      order = cd.svgOrder('M',[[width,startY]]) + cd.svgOrder('C',[[width-30,startY],[30,endY],[0,endY]]);
    }
    
    $branchLine.attr('d', order );
    $branchInLine.attr('d', order );
    $branchOutLine.attr('d', order );
    $branchBackLine.attr('d', order );
  });
    
}
/*
##################################################
   ノード分岐追加・削除
##################################################
*/
statuFileBranchBodyHTML( index, elseFlag, value ){
    if ( index === undefined ) index = 2;
    if ( value === undefined ) value = '';
    value = $('<div/>', {'text': value }).html();

    let html = '<div class="node-body">';
    if ( elseFlag === true ) {
      html += '<div class="branch-if-type branch-if-else">else</div>';
    } else {
      const ifText = ( Number( index ) === 1 )? 'if': 'else if';
      html += '<div class="branch-if-type">' + ifText + '</div>'
      + '<div class="branch-if-body"><span class="branch-if-value"><span class="branch-if-value-inner">' + value + '</span></span></div>';
    }
    html += '</div>';
    return html;
}
/*
##################################################
   分岐追加
##################################################
*/
addBranch( nodeID ) {
    const cd = this;
    
    const $branchNode = $('#' + nodeID );
    let branchType = '',
        nodeHTML = '<div class="node-sub">';
    
    if ( $branchNode.is('.function-conditional') ) {
      branchType = 'conditional';
      nodeHTML += ''
          + '<div class="branch-cap branch-in"></div>'
          + '<div class="node-body">'
            + '<div class="branch-type"><ul></ul></div>'
          + '</div>'
          + cd.createTerminalHTML('out', 'terminal-' + cd.count.terminal );
    } else if ( $branchNode.is('.function-parallel') ) {
      branchType = 'parallel';
      nodeHTML += ''
          + '<div class="branch-cap branch-in"></div>'
          + cd.createTerminalHTML('out', 'terminal-' + cd.count.terminal );
    } else if ( $branchNode.is('.function-status-file') ) {
      branchType = 'status-file';
      nodeHTML += ''
          + '<div class="branch-cap branch-in"></div>'
          + cd.statuFileBranchBodyHTML()
          + cd.createTerminalHTML('out', 'terminal-' + cd.count.terminal );
    } else if ( $branchNode.is('.function-merge') ) {
      branchType = 'merge';
      nodeHTML += ''
          + cd.createTerminalHTML('in', 'terminal-' + cd.count.terminal )
          + cd.mergeStatusHTML()
          + '<div class="merge-cap merge-out"></div>';
    }
    nodeHTML += '</div>';
    
    if ( branchType !== '' ) {
      // 条件分岐は最大6分岐までにする
      const branchLength = $branchNode.find('.node-sub').length;
      if ( !( branchType === 'conditional' && branchLength > 6 ) ) {
        cd.count.terminal++;

        if ( branchType === 'conditional' || branchType === 'status-file' ) {
          $branchNode.find('.node-sub.default').before( nodeHTML );
        } else if ( branchType === 'parallel' ) {
          $branchNode.find('.node-branch').append( nodeHTML );
        } else {
          $branchNode.find('.node-' + branchType ).append( nodeHTML );
        }
        
        const beforeNodeData = $.extend( true, {}, cd.data[ nodeID ] );
        cd.nodeSet( $branchNode );
        const afterNodeData = $.extend( true, {}, cd.data[ nodeID ] );
        cd.conductorHistory().branch( beforeNodeData, afterNodeData );
        
        cd.panelChange( nodeID );
        cd.branchLine( nodeID );
        cd.connectEdgeUpdate( nodeID );
      } else {
        cd.message('0002');
      }
    }
}
/*
##################################################
   分岐削除
##################################################
*/
removeBranch( nodeID, terminalID ) {
    const cd = this;

    const $branchNode = $('#' + nodeID );
    let branchType = '';
    if ( $branchNode.is('.function-conditional') ) {
      branchType = 'conditional';
    } else if ( $branchNode.is('.function-parallel') ) {
      branchType = 'parallel';
    } else if ( $branchNode.is('.function-status-file') ) {
      branchType = 'status-file';
    } else if ( $branchNode.is('.function-merge') ) {
      branchType = 'merge';
    }
    
    if ( branchType !== '' ) {
      const branchNum = $branchNode.find('.node-sub').length,
            connectNum = $branchNode.find('.node-sub .connected').length;
      
      // 分岐は最低２つ
      if ( branchNum > 2 ) {
      
        // 未接続の分岐があるか？
        if ( branchNum !== connectNum ) {

          let $targetTerminal;
          // terminalIDが未定義なら最後の未接続の要素
          if ( terminalID === undefined ) {
            $targetTerminal = $branchNode.find('.node-terminal').not('.connected').closest('.node-sub').not('.default').eq(-1);
            if ( !$targetTerminal.length ) return false;
            terminalID = $targetTerminal.find('.node-terminal').attr('id');
          } else {
            $targetTerminal.find('#' + terminalID ).closest('.node-sub');
          }

          const caseNum = cd.data[ nodeID ].terminal[ terminalID ].case,
                $deleteCase = $('#branch-case-list').find('tbody').find('tr').eq( caseNum - 1 );

          // 削除するケースに条件があるか？
          if ( $deleteCase.find('li').length ) {
            // 削除される条件をOtherに移動する
            $deleteCase.find('li').prependTo( $('#noset-conditions') );
          }
          $deleteCase.remove();

          delete cd.data[ nodeID ].terminal[ terminalID ];
          $targetTerminal.remove();
          
          cd.branchLine( nodeID );
          const beforeNodeData = $.extend( true, {}, cd.data[ nodeID ] );
          cd.nodeSet( $branchNode );
          const afterNodeData = $.extend( true, {}, cd.data[ nodeID ] );
          cd.conductorHistory().branch( beforeNodeData, afterNodeData );
          cd.panelChange( nodeID );
          cd.connectEdgeUpdate( nodeID );

          // Status file branchで削除したのが最初のTerminalの場合名称を修正する
          if ( caseNum === 1 && branchType === 'status-file') {
            $branchNode.find('.branch-if-type').eq(0).text('if');
          }

        } else {
          cd.message('0004');
        }
      
      } else {
        cd.message('0003');
      }
      
    }
}
/*
##################################################
   位置情報登録
##################################################
*/
nodeSet( $node, x, y ){
    const cd = this;

    const nodeID = $node.attr('id'),
          w = $node.width(),
          h = $node.height();
    
    // x と y が未定義なら位置情報を更新しない
    if ( x !== undefined && y !== undefined ) {
      
      // 念のため数値化
      x = Number( x );
      y = Number( y );
    
      // アートボードの中か？
      if ( x < 1 ) x = 0;
      if ( x + w > cd.editor.artBoard.w ) x = cd.editor.artBoard.w - w;
      if ( y < 1 ) y = 0;
      if ( y + h > cd.editor.artBoard.h ) y = cd.editor.artBoard.h - h;

      // 位置確定
      $node.css({
        'left' : x,
        'top' : y,
        'transform' : 'none'
      });

      cd.data[ nodeID ].x = x;
      cd.data[ nodeID ].y = y;
    
    }
    
    cd.data[ nodeID ].w = w;
    cd.data[ nodeID ].h = h;

    // ターミナルの位置情報更新
    let branchCount = 1;
    $node.find('.node-terminal').each( function() {
        const $terminal = $( this ),
              terminalID = $terminal.attr('id'),
              terminalWidth = $terminal.outerWidth() / 2,
              terminalHeight = $terminal.outerHeight() / 2;

        // 未定義なら初期化
        if ( cd.data[ nodeID ].terminal[ terminalID ] === undefined ) {
            cd.data[ nodeID ].terminal[ terminalID ] = {};
            if ( $terminal.is('.node-in') ) {
                cd.data[ nodeID ].terminal[ terminalID ].type = 'in';
            } else {
                cd.data[ nodeID ].terminal[ terminalID ].type = 'out';
            }
        }

        const nodeType = cd.data[ nodeID ].type,
              terminalType = cd.data[ nodeID ].terminal[ terminalID ].type;

        // 分岐ノードの情報をセット
        if (
            ( nodeType === 'conditional-branch' && terminalType === 'out' ) ||
            ( nodeType === 'parallel-branch' && terminalType === 'out' ) ||
            ( nodeType === 'status-file-branch' && terminalType === 'out' ) ||
            ( nodeType === 'merge' && terminalType === 'in' )
        ) {
          // 条件分岐Case情報をセット
          if ( nodeType === 'conditional-branch' ) {
              let branchArray = [];
              $terminal.prev('.node-body').find('li').each( function(){
                  branchArray.push( $( this ).attr('data-end-status') );
              });
              cd.data[ nodeID ].terminal[ terminalID ].condition = branchArray;
          }
          
          if ( cd.data[ nodeID ].terminal[ terminalID ].case !== 'else') {
              cd.data[ nodeID ].terminal[ terminalID ].case = branchCount++;
          }
        }

        cd.data[ nodeID ].terminal[ terminalID ].id = terminalID;
        cd.data[ nodeID ].terminal[ terminalID ].x =
            Math.round( Number( cd.data[ nodeID ].x ) + $terminal.position().left / cd.editor.scaling + terminalWidth );
        cd.data[ nodeID ].terminal[ terminalID ].y =
            Math.round( Number( cd.data[ nodeID ].y ) + $terminal.position().top / cd.editor.scaling + terminalHeight );
    });
    
}
/*
##################################################
   ノードジェムのテキストが溢れているか
##################################################
*/
nodeGemCheck( $node ) {
    const $gem = $node.find('.node-gem');
    if ( $gem.length ) {
        const gemWidth = $gem.width(),
              gemTextWidth = $gem.find('.node-gem-inner').width();
        if ( gemWidth < gemTextWidth ) {
            const scale = Math.floor( gemWidth / gemTextWidth * 1000 ) / 1000;
            $node.find('.node-gem-inner').css('transform','translateX(-50%) scale(' + scale + ')');
        }
    }
}
/*
##################################################
   ノードを指定位置に移動する
##################################################
*/
nodeMoveSet( nodeID, x, y, position ) {
    const cd = this;
  
    if ( position === undefined ) position = 'absolute';
    if ( position === 'relative' ) {
        if ( Array.isArray( nodeID ) ) {
            const nodeIdLength = nodeID.length;
            let nodeEdgeArray = [];
            for ( let i = 0; i < nodeIdLength; i++ ) {
                const moveX = Number( cd.data[ nodeID[i] ].x ) + x,
                      moveY = Number( cd.data[ nodeID[i] ].y ) + y;
                for ( let terminalID in cd.data[ nodeID[i] ]['terminal'] ) {
                    const terminal = cd.data[ nodeID[i] ]['terminal'][ terminalID ];
                    if ( 'edge' in terminal ) {
                        const edgeID = cd.data[ terminal['edge'] ]['id'];
                      if ( nodeEdgeArray.indexOf( edgeID ) === -1 ) {
                          nodeEdgeArray.push( edgeID );
                      }
                  }
              }
              cd.nodeSet( $('#' + nodeID[i] ), moveX, moveY );
          }
          const nodeEdgeLength = nodeEdgeArray.length;
          for ( let i = 0; i < nodeEdgeLength; i++ ) {
              cd.edgeUpdate( nodeEdgeArray[i] );
          }      
        } else {
          const moveX = Number( cd.data[ nodeID ].x ) + x,
                moveY = Number( cd.data[ nodeID ].y ) + y;
          cd.nodeSet( $('#' + nodeID ), moveX, moveY );
          cd.connectEdgeUpdate( nodeID );
        }
    } else {
        cd.nodeSet( $('#' + nodeID ), x, y );
        cd.connectEdgeUpdate( nodeID );
    }
}
/*
##################################################
   キャンバスの表示されている部分から位置を設定
##################################################
*/
visiblePosition( axis, position, width, height ) {
    const cd = this;

    const adjustPosition = 32; // 調整する端からの距離

    let positionNumber = 0;

    switch( position ) {
      case 'center':
        if ( axis === 'x' ) positionNumber = - cd.editor.canvasPt.x - cd.editor.artBoardPt.x + ( cd.editor.area.w / 2 ) - ( width / 2 );
        if ( axis === 'y' ) positionNumber = - cd.editor.canvasPt.y - cd.editor.artBoardPt.y + ( cd.editor.area.h / 2 ) - ( height / 2 );
        break;
      case 'top':
        if ( axis === 'y' ) positionNumber = - cd.editor.canvasPt.y - cd.editor.artBoardPt.y + adjustPosition;
        break;
      case 'bottom':
        if ( axis === 'y' ) positionNumber = - cd.editor.canvasPt.y - cd.editor.artBoardPt.y + cd.editor.area.h - height - adjustPosition;
        break;
      case 'left':
        if ( axis === 'x' ) positionNumber = - cd.editor.canvasPt.x - cd.editor.artBoardPt.x + adjustPosition;
        break;
      case 'right':
        if ( axis === 'x' ) positionNumber = - cd.editor.canvasPt.x - cd.editor.artBoardPt.x + cd.editor.area.w - width - adjustPosition;
        break;
    }

    return positionNumber;
}
/*
##################################################
   New node set
##################################################
*/
newNode( type, x, y ) {
    const cd = this;

    const $node = cd.initialNode( type );

    // アートボードにNode追加
    cd.$.artBoard.append( $node );

    // 要素の追加を待つ
    $node.ready( function(){

      const width = $node.width(),
            height = $node.height();

      // x, yが数値以外の場合
      if ( fn.typeof( x ) !== 'Number') x = cd.visiblePosition('x', x, width, height );
      if ( fn.typeof( y ) !== 'Number') y = cd.visiblePosition('y', y, width, height );

      // 位置情報をセット
      cd.nodeSet( $node, x, y );
    });
}
/*
##################################################
   登録済みの線を再描画する（読み込み時など）
##################################################
*/
edgeDraw( edgeID ) {
    const cd = this;

    const $edge = cd.newSVG( edgeID );
    $edge.attr('data-connected', 'connected');

    const outNodeID = cd.data[ edgeID ].outNode,
          outTerminalID = cd.data[ edgeID ].outTerminal,
          inNodeID = cd.data[ edgeID ].inNode,
          inTermianlID = cd.data[ edgeID ].inTerminal;

    $('#' + outTerminalID ).addClass('connected');
    $('#' + inTermianlID ).addClass('connected');
    
    const outX = Number( cd.data[ outNodeID ].terminal[ outTerminalID ].x ),
          outY = Number( cd.data[ outNodeID ].terminal[ outTerminalID ].y ),
          inX = Number( cd.data[ inNodeID ].terminal[ inTermianlID ].x ),
          inY = Number( cd.data[ inNodeID ].terminal[ inTermianlID ].y );

    $edge.find('path').attr('d', cd.svgDrawPosition( outX, outY, inX, inY ) );
}
/*
##################################################
   登録済みの線を再描画する（Undo/Redo）
##################################################
*/
edgeConnect( edgeID ) {
    const cd = this;

    const outNodeID = cd.data[ edgeID ].outNode,
          outTerminalID = cd.data[ edgeID ].outTerminal,
          inNodeID = cd.data[ edgeID ].inNode,
          inTermianlID = cd.data[ edgeID ].inTerminal;

    // 接続状態を紐づけする
    cd.data[ outNodeID ]['terminal'][ outTerminalID ].targetNode = inNodeID;
    cd.data[ outNodeID ]['terminal'][ outTerminalID ].edge = edgeID;
    cd.data[ inNodeID ]['terminal'][ inTermianlID ].targetNode = outNodeID;
    cd.data[ inNodeID ]['terminal'][ inTermianlID ].edge = edgeID;

    cd.edgeDraw( edgeID );
}
/*
##################################################
   connectEdgeID = 'new'で新規
##################################################
*/
nodeConnect( connectEdgeID, outNodeID, outTerminalID, inNodeID, inTermianlID ) {
    const cd = this;

    let $edge, edgeID;

    if ( connectEdgeID === 'new'){
      $edge = cd.newSVG();
      edgeID = $edge.attr('id');
    } else {
      $edge = $('#' + connectEdgeID );
      edgeID = connectEdgeID
    }
    $edge.attr('data-connected','connected');

    // 登録の無いEdgeの場合登録する
    if ( !( 'edge' in cd.data ) ) {
      cd.data[ edgeID ] = {
        'type' : 'edge',
        'id' : edgeID
      };
    }

    const $outTerminal =  $('#' + outTerminalID ),
          $inTerminal = $('#' + inTermianlID );
    $outTerminal.add( $inTerminal ).addClass('connected');

    // 接続状態を紐づけする
    cd.data[ outNodeID ]['terminal'][ outTerminalID ].targetNode = inNodeID;
    cd.data[ outNodeID ]['terminal'][ outTerminalID ].edge = edgeID;
    cd.data[ inNodeID ]['terminal'][ inTermianlID ].targetNode = outNodeID;
    cd.data[ inNodeID ]['terminal'][ inTermianlID ].edge = edgeID;

    // Edge
    cd.data[ edgeID ].outNode = outNodeID;
    cd.data[ edgeID ].outTerminal = outTerminalID;
    cd.data[ edgeID ].inNode = inNodeID;
    cd.data[ edgeID ].inTerminal = inTermianlID;

    // newの場合結線する
    if ( connectEdgeID === 'new'){
      const outX = Number( cd.data[ outNodeID ].terminal[ outTerminalID ].x ),
            outY = Number( cd.data[ outNodeID ].terminal[ outTerminalID ].y ),
            inX = Number( cd.data[ inNodeID ].terminal[ inTermianlID ].x ),
            inY = Number( cd.data[ inNodeID ].terminal[ inTermianlID ].y );
      $edge.find('path').attr('d', cd.svgDrawPosition( outX, outY, inX, inY ) );
    }

    return edgeID;

}
/*
##################################################
   接続できるターミナルチェック
##################################################
*/
edgeConnectCheck( currentNodeID, inOut ) {
    const cd = this;
        
    let conectCount = 0;
    for ( let nodeID in cd.data ) {
      if ( RegExp('^node-').test( nodeID ) && nodeID !== currentNodeID ) {
        
        let outNodeID, inNodeID, targetTerminal;
        
        if ( inOut === 'out-in') {
          outNodeID = currentNodeID;
          inNodeID = nodeID;
          targetTerminal = 'in';
        } else if( inOut === 'in-out') {
          outNodeID = nodeID;
          inNodeID = currentNodeID;
          targetTerminal = 'out';
        }
        
        // 接続可能チェック
        if ( cd.checkConnectType( cd.data[ outNodeID ].type, cd.data[ inNodeID ].type ) ) {
          const terminals = cd.terminalInOutID( cd.data[ nodeID ].terminal, targetTerminal ),
                terminalLength = terminals.length;
          for ( let i = 0; i < terminalLength; i++ ) {
            if ( !('targetNode' in cd.data[ nodeID ].terminal[ terminals[ i ] ] ) ) {
              $('#' + terminals[ i ] ).addClass('wait-connect');
              conectCount++;
            }
          } 
        }
        
      }
    }
    if ( conectCount === 0 ) cd.message('0001');
}
/*
##################################################
   接続できるターミナルチェッククリア
##################################################
*/
edgeConnectCheckClear() {
    this.$.area.find('.wait-connect').removeClass('wait-connect');
}
/*
##################################################
   割り込み出来る線かどうかチェックする
##################################################
*/
nodeInterruptCheck( nodeID ) {
    const cd = this;
    
    // 割り込みしないノード
    const exclusionNode = ['start', 'end'];
    if ( exclusionNode.indexOf( cd.data[ nodeID].type ) !== -1 ) return false;
    
    // 複数選択されていたら終了
    if ( cd.select.length > 1 ) return false; 
    
    // 1つでも接続済みであれば終了
    const $node = $('#' + nodeID );
    if ( $node.find('.connected').length ) return false;
    
    // 全ての線をチェック
    for ( let edgeID in cd.data ) {
      if ( RegExp('^line-').test( edgeID ) ) {
        const outNodeID = cd.data[ edgeID ].outNode,
              inNodeID = cd.data[ edgeID ].inNode;
        if (
          cd.checkConnectType( cd.data[ outNodeID ].type, cd.data[ nodeID ].type ) &&
          cd.checkConnectType( cd.data[ nodeID ].type, cd.data[ inNodeID ].type )
        ) {
          $('#' + edgeID ).attr('data-interrupt', 'true');
        }
      }
    }
}
/*
##################################################
   割り込み出来る線チェッククリア
##################################################
*/
nodeInterruptCheckClear() {
    $('.svg-group').filter('[data-interrupt="true"]').removeAttr('data-interrupt');
}
/*
##################################################
   結線に割り込む
##################################################
*/
nodeInterrupt( nodeID ) {
    const cd = this;
   
    const $hoverEdge = $('.svg-group[data-interrupt="true"].hover');
    if ( $hoverEdge.length ) {
            
      const hoverEdgeID = $hoverEdge.attr('id'),
            edgeData = cd.data[ hoverEdgeID ];
      
      let outTerminalID, inTerminalID;
      
      const outTerminals = cd.terminalInOutID( cd.data[ nodeID ].terminal, 'out'),
            outTerminalLength = outTerminals.length,
            inTerminals = cd.terminalInOutID( cd.data[ nodeID ].terminal, 'in'),
            inTerminalLength = inTerminals.length;

      // 分岐ノードはCase1に接続する
      const branchNodeCheck = ['parallel-branch', 'conditional-branch', 'status-file-branch'];
      if ( branchNodeCheck.indexOf( cd.data[ nodeID ].type ) !== -1 ) {
        for ( let i = 0; i < outTerminalLength; i++ ) {
          if ( Number( cd.data[ nodeID ]['terminal'][ outTerminals[ i ] ].case ) === 1 ) {
            outTerminalID = outTerminals[ i ];
            break;
          }
        }
      } else {
        outTerminalID = outTerminals[0];
      }
      if ( cd.data[ nodeID ].type === 'merge' ) {
        for ( let i = 0; i < inTerminalLength; i++ ) {
          if ( Number( cd.data[ nodeID ]['terminal'][ inTerminals[ i ] ].case ) === 1 ) {
            inTerminalID = inTerminals[ i ];
            break;
          }
        }
      } else {
        inTerminalID = inTerminals[0];
      }
      
      // conductorHistory用に削除するedgeをコピーしておく
      const removeEdgeData = $.extend( true, {}, cd.data[ hoverEdgeID ] );
      
      // Delete Edge
      cd.removeEdge( hoverEdgeID, 0 );
      // target Out > current Node In
      const newEdge1 = cd.nodeConnect('new', edgeData.outNode, edgeData.outTerminal, nodeID, inTerminalID );
      // current Node Out > target In
      const newEdge2 = cd.nodeConnect('new', nodeID, outTerminalID, edgeData.inNode, edgeData.inTerminal );
      
      cd.conductorHistory().interrupt( removeEdgeData, newEdge1, newEdge2 );
      
      // 割り込みしたら True
      return true;
    } else {
      return false;
    }
}
/*
##################################################
   ノード選択
##################################################
*/
nodeSelect( nodeID ) {
    const cd = this;
    
    const $nodeDelete = cd.$.header.find('.editor-menu-button[data-menu="node-delete"]');
    
    // nodeIDが未指定の場合すべての要素を選択
    if ( nodeID === undefined ) {
    
      for ( let key in cd.data ) {
        if ( RegExp('^node-').test( key ) ) {
          cd.nodeSelect( key );
        }
      }
      cd.panelChange();
    
    } else {
    
      const $node = $('#' + nodeID );
      $node.addClass('selected');

      // 選択中のノード一覧
      if ( cd.select.indexOf( nodeID ) === -1 ) {
        cd.select.push( nodeID );
      }

      if ( !( cd.select[0] === 'node-1' && cd.select.length === 1 ) ) {
        $nodeDelete.prop('disabled', false );
      }

      if ( cd.setting.debug === true ) {
        window.console.group('Select node list');
        window.console.log( cd.select );
        window.console.groupEnd('Select node list');
      }
    
    }
    
}
/*
##################################################
   ノード選択解除
##################################################
*/
nodeDeselect( nodeID ) {
    const cd = this;
    
    const $nodeDelete = cd.$.header.find('.editor-menu-button[data-menu="node-delete"]');
    
    if ( nodeID === undefined ) {
      // nodeID が未指定の場合すべての選択を解除
      cd.select = [];
      $('.node.selected').removeClass('selected');
    } else {
      // 指定IDの選択を解除
      const deselectNo = cd.select.indexOf( nodeID );
      if ( deselectNo !== -1 ) {
        cd.select.splice( deselectNo, 1 );
        $('#' + nodeID ).removeClass('selected');
      }
    }
    
    if ( !cd.select.length || ( cd.select[0] === 'node-1' && cd.select.length === 1 ) ) {
      $nodeDelete.prop('disabled', true );
    }
}
/*
##################################################
   ノード削除
##################################################
*/
nodeRemove( nodeID ) {
    const cd = this;
    
    const nodeRemoveFunc = function( removeNodeID ) {
      // 接続している線があれば削除する
      if ( 'terminal' in  cd.data[ removeNodeID ] ) {
        const terminals = cd.data[ removeNodeID ].terminal;
        for ( let terminal in terminals ) {
          const terminalData = terminals[ terminal ];
          if ( 'edge' in terminalData ) {
            const edge = cd.data[ terminalData.edge ];
            cd.removeEdge( edge.id, 0 );
          }
        }
      }
      // Start（id="node-1"）は削除しない
      if ( removeNodeID !== 'node-1' ) {
        // ノード削除
        $('#' + removeNodeID ).remove();
        delete cd.data[ removeNodeID ];
        cd.panelChange();
      } else {
        // message('0006');
      }
    }
    
    // 配列かどうか判定
    if ( $.isArray( nodeID ) ) {
      const nodeLength = nodeID.length;
      if ( nodeLength ) {
        for ( let i = 0; i < nodeLength; i++ ) {
          nodeRemoveFunc( nodeID[ i ] );
        }
      }
    
    } else {
      nodeRemoveFunc( nodeID );
    }
    
    // 選択を解除する
    cd.nodeDeselect();
    cd.panelChange();
    
    cd.updateConductorData();
}
/*
##################################################
   接続可能チェック（接続できる＝True）
##################################################
*/
checkConnectType( outType, inType ) {
    const cd = this;
    if ( outType in cd.setting.connectablePattern &&
         cd.setting.connectablePattern[ outType ].indexOf( inType ) !== -1 ) {    
        return false;
    } else {
        return true;
    }
}
/*
##################################################
   結線調査開始ノードID一覧を返す
##################################################
*/
conditionalBranchID() {
    const cd = this;
          
    let conditionalBranchIdList = [];
    for ( const nodeID in cd.data ) {
      if ( cd.data[ nodeID ].type === 'conditional-branch' || cd.data[ nodeID ].type === 'start') {
          conditionalBranchIdList.push( nodeID );
      }
    }

    // 条件分岐以外の開始ノードを条件分岐をさかのぼって調べる
    const startNodeCheck = function( nodeID ) {
      if ( cd.data[ nodeID ].type === "merge" ) return false;
      const terminals = cd.terminalInOutID( cd.data[ nodeID ]['terminal'], 'in'),
            terminalLength = terminals.length;
      for ( let i = 0; i < terminalLength; i++ ) {
        const terminal = cd.data[ nodeID ]['terminal'][ terminals[i] ];
        if ('targetNode' in terminal ) {
          startNodeCheck( terminal.targetNode );
        } else {
          if ( conditionalBranchIdList.indexOf( nodeID ) === -1 ) {
            conditionalBranchIdList.push( nodeID );
          }
        }
      }
    };
    const conditionalBranchength = conditionalBranchIdList.length;
    for ( let i = 0; i < conditionalBranchength; i++ ) {
      startNodeCheck( conditionalBranchIdList[ i ] );
    }

    return conditionalBranchIdList;
}
/*
##################################################
   結線調査
##################################################
*/
nodeConditionalToMergeCheck() {
    const cd = this;

    let nodeConditionalToMergeFlag = true,
        mergeCheckArray = {};
    const conditionalBranches = cd.conditionalBranchID(),
          conditionalBranchLenght = conditionalBranches.length;

    const nodeConditionalToMergeRecursion = function( nodeID, conditionalID, parallelBranchFlag ) {
        const terminals = cd.terminalInOutID( cd.data[ nodeID ]['terminal'], 'out'),
              terminalLength = terminals.length;
        if ( cd.data[ nodeID ].type === 'parallel-branch') parallelBranchFlag = true;
        if ( cd.data[ nodeID ].type === 'merge') {
          if ( parallelBranchFlag === true ) {
            if ( nodeID in mergeCheckArray ) {
              if ( mergeCheckArray[ nodeID ] !== conditionalID ) {
                cd.message('0007');
                nodeConditionalToMergeFlag = false;
              }
            } else {
              mergeCheckArray[ nodeID ] = conditionalID;
            }
          } else {
            cd.message('0007');
            nodeConditionalToMergeFlag = false;
          }
        }

        if ( nodeConditionalToMergeFlag !== false ) {
          for ( let i = 0; i < terminalLength; i++ ) {
            const terminal = cd.data[ nodeID ]['terminal'][ terminals[i] ];
            if ('targetNode' in terminal ) {
              const targetNodeID = terminal.targetNode,
                    targetNodeType = cd.data[ targetNodeID ].type;
              if ( targetNodeType !== 'conditional-branch') {
                if ( cd.data[ nodeID ].type === 'conditional-branch') {
                  nodeConditionalToMergeRecursion( targetNodeID, terminals[i], false );
                } else {
                  nodeConditionalToMergeRecursion( targetNodeID, conditionalID, parallelBranchFlag );
                }
              }
            }
          }
        }
    }
  
    for ( let i = 0; i < conditionalBranchLenght; i++ ) {
      nodeConditionalToMergeRecursion( conditionalBranches[ i ] );
    }

    return nodeConditionalToMergeFlag;
}
/*
##################################################
   結線時ノードループ調査
##################################################
*/
nodeLoopCheck( nodeID ) {
    const cd = this;

    let flag = true,
        nodeArray = [],
        mergeArray = [];

    // 重複にカウントしないノード
    const noCountNode = [
      'conditional-branch',
      'parallel-branch',
      'status-file-branch',
      'merge'
    ];

    if ( cd.setting.debug === true ) window.console.log('----- Route check -----');

    const nodeLoopCheckRecursion = function( next ) {
      if ( flag === true ) {
        const node = cd.data[ next ];

        // 経路ログ
        if ( cd.setting.debug === true ) {
          window.console.log( 'ID:' + next + ' / ' + node.type );
        }

        if ( noCountNode.indexOf( node.type ) === -1 ) {
          nodeArray.push( next );
        }

        // ターミナルの数だけループ
        for ( let terminals in node.terminal ) {
          if ( node.terminal[ terminals ].type === 'out' && 'targetNode' in node.terminal[ terminals ] ) {
            next = node.terminal[ terminals ].targetNode;
            // すでに通過したマージの先はチェックしない
            if ( mergeArray.indexOf( next ) === -1 ) {
              // 同じIDが見つかれば終了
              if ( nodeArray.indexOf( next ) !== -1 ) {
                flag = false;
                cd.message('0005');
                return false;
              } else if ( next !== undefined ) {
                // 次があれば再帰
                nodeLoopCheckRecursion( next );
              }
            }
          }
        }

        if ( 'merge' === node.type ) {
          mergeArray.push( next );
        }
      }
    };
    nodeLoopCheckRecursion( nodeID );
    return flag;  
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   パネル関連
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

/*
##################################################
  パネル初期設定
##################################################
*/
initPanel() {
    const cd = this;
    
    // 終了ステータス
    cd.status = {};
    cd.status.end = {
      '5': ['done', '正常'], // 正常
      '11': ['warning', '警告'], // 警告
      '7': ['error', '異常'] // 異常
    };
    
    // 初期パネルをセットする
    cd.setInitPanel();
    
    // Movementリスト
    cd.movementList();
    
    cd.$.conductorParameter = $('#conductor-parameter > .editor-block-inner'),
    cd.$.statusFileCaseList = $('#status-file-case-list').find('tbody');
    
    // 整列
    cd.nodeAlignment();
    
    // パネルイベント
    cd.panelEvents();
}
/*
##################################################
  初期パネルをセット
##################################################
*/
setInitPanel() {
    const cd = this;
    
    const html = `
    <div id="conductor-parameter" class="editor-block">
        <div class="editor-block-inner">
        </div>
    </div>
    <div class="editor-row-resize-bar"></div>
    <div id="conductor-node" class="editor-block">
        <div class="editor-block-inner">
            <div class="editor-tab">
                <div class="editor-tab-menu">
                    <ul class="editor-tab-menu-list">
                          <li class="editor-tab-menu-item" data-tab="movement-list">Movement</li>
                          <li class="editor-tab-menu-item" data-tab="function-list">Function</li>
                    </ul>
                </div>
                <div class="editor-tab-contents">
                    <div id="movement-list" class="editor-tab-body">
                        <div class="editor-tab-body-inner">
                            ${cd.movementListHtml()}
                        </div>
                    </div>
                    <div id="function-list" class="editor-tab-body">
                        <div class="editor-tab-body-inner">
                            ${cd.functionListHtml()}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    
    cd.$.panel.html( html );
}
/*
##################################################
  パネルをセット
##################################################
*/
setPanel( type, nodeId ) {
    const cd = this;

    let html = '';
    switch( type ) {
        case 'conductor':
            html = cd.panelConductorHtml( nodeId );
        break;
        case 'movement':
            html = cd.panelMovementHtml( nodeId );
        break;
        case 'end':
            html = cd.panelEndHtml( nodeId );
        break;
        case 'conditional-branch':
            html = cd.panelConditionalBranchHtml( nodeId );
        break;
        case 'parallel-branch':
            html = cd.panelParallelBranchHtml( nodeId );
        break;
        case 'status-file-branch':
            html = cd.panelStatusBranchHtml( nodeId );
        break;
        case 'merge':
            html = cd.panelMergeHtml( nodeId );
        break;
        case 'call':
            html = cd.panelCallHtml( nodeId );
        break;
        case 'start':
            html = cd.panelCommonHtml( nodeId, 'Conductor start');
        break;
        case 'pause':
            html = cd.panelCommonHtml( nodeId, 'Conductor pause');
        break;
        case 'alignment':
            html = cd.panelAlignmentHtml();
        break;
    }
    cd.$.conductorParameter.html( html );
}
/*
##################################################
   Movementリスト
##################################################
*/
movementListHtml() {
    return `
    <div class="movement-filter">
      <table class="panel-table">
        <tbody>
          <tr class="movement-filter-row">
            <th class="panel-th">Name Filter :</th>
            <td class="panel-td"><input id="movement-filter" class="panel-text" type="text" placeholder="Movement Name"><span class="filter-setting-btn" title="Filter setting"></span></td>
          </tr>
          <tr class="movement-filter-id-row">
            <th class="panel-th">ID Filter :</th>
            <td class="panel-td"><input id="movement-filter-id" class="panel-text" type="text" placeholder="Movement ID"><span class="filter-setting-btn" title="Filter setting"></span></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="node-table-wrap">
      <table class="node-table">
        <thead>
          <tr>
            <th class="movement-list-orchestrator" title="Orchestrator"><div class="movement-list-sort" data-sort="orchestra_id" data-sort-type="number">+</div></th>
            <th class="movement-list-name" title="Movement Name"><div class="movement-list-sort" data-sort="PATTERN_NAME" data-sort-type="string">Movement name</div></th>
          </tr>
        </thead>
        <tbody id="movement-list-rows">
        </tbody>
      </table>
    </div>
    <div id="movement-filter-setting">
      <div class="movement-filter-setting-inner">
        <div class="movement-filter-setting-body">
          <div class="panel-group">
            <div class="panel-group-title">Filter setting</div>
            <ul class="movement-filter-setting-list">
              <li><label class="property-label"><input type="radio" name="filter-target" id="filter-target-id"> </label></li>
              <li><label class="property-label"><input type="radio" name="filter-target" id="filter-target-name" checked> Movement Name</label></li>
            </ul>
          </div>
          <div class="panel-group">
            <div class="panel-group-title">Orchestrator select</div>
            <ul id="orchestrator-list" class="movement-filter-setting-list">
            </ul>
          </div>
        </div>
        <div class="movement-filter-setting-footer">
          <ul class="panel-button-group">
            <li class="panel-button-group-item"><button id="movement-filter-ok" class="positive panel-button">設定</button></li>
            <li class="panel-button-group-item"><button id="movement-filter-cancel" class="negative panel-button">キャンセル</button></li>
          </ul>
        </div>
      </div>
    </div>`;
}
/*
##################################################
  Functionリスト
##################################################
*/
functionListHtml() {
    return `
    <div class="node-table-wrap">
        <table class="node-table">
            <thead>
                <tr><th><div>+</div></th><th><div>Function type</div></th></tr>
            </thead>
            <tbody>
                <tr><th><span class="add-node function" data-function-type="end"></span></th><td><div>Conductor end</div></td></tr>
                <tr><th><span class="add-node function" data-function-type="pause"></span></th><td><div>Conductor pause</div></td></tr>
                <tr><th><span class="add-node function" data-function-type="call"></span></th><td><div>Conductor call</div></td></tr>
                <tr><th><span class="add-node function" data-function-type="conditional-branch"></span></th><td><div>Conditional branch</div></td></tr>
                <tr><th><span class="add-node function" data-function-type="parallel-branch"></span></th><td><div>Parallel branch</div></td></tr>
                <tr><th><span class="add-node function" data-function-type="merge"></span></th><td><div>Parallel merge</div></td></tr>
                <tr><th><span class="add-node function" data-function-type="status-file-branch"></span></th><td><div>Status file branch</div></td></tr>
            </tbody>
        </table>
    </div>`;
}
/*
##################################################
  パネル基本
##################################################
*/
panelCommon( title, body ) {
    return `
    <div class="editor-panel-block">
        <div class="editor-panel-title">
            <div class="editor-panel-title-inner">
                ${title}
            </div>
        </div>
        <div class="editor-panel-body">
            <div class="editor-panel-body-inner">
                ${body}
            </div>
        </div>
    </div>`;
}
/*
##################################################
  備考欄基本
##################################################
*/
panelTextareaHtml( note ) {
    const cd = this;
    return `
    <div class="panel-group">
        <div class="panel-group-title">Note</div>
        ${( cd.mode !== 'edit' && cd.mode!== 'update')?
            `<span class="view panel-note panel-span"></span>`:
            `<textarea title="タイトル説明" class="panel-note panel-textarea" spellcheck="false">${note}</textarea>`
        }
    </div>`;
}

/*
##################################################
  Conductor情報パネル
##################################################
*/
panelConductorHtml() {
    const cd = this;
    
    const condcutor = cd.data.conductor,
          id = fn.cv( condcutor.id, '', true ),
          name = fn.cv( condcutor.conductor_name, '', true ),
          note = fn.cv( condcutor.note, '', true ),
          update = fn.cv( condcutor.last_update_date_time, '', true );

    const html = `
    <table class="panel-table">
        <tbody>
            <tr>
                <th class="panel-th">ID :</th>
                <td class="panel-td" colspan="2">
                    <span class="panel-span">${id}</span>
                </td>
            </tr>
            <tr ${( cd.mode === 'edit' || cd.mode === 'update')? `class="popup" title="タイトル説明"`: ''}>
                <th class="panel-th">名称 :</th>
                <td class="panel-td" colspan="2">
                    ${( cd.mode !== 'edit' && cd.mode !== 'update')?
                        `<span class="view panel-span">${name}</span>`:
                        `<input value="${name}" maxlength="256" id="conductor-class-name" class="panel-text" type="text">`
                    }
                </td>
            </tr>
            <tr>
                <th class="panel-th">更新日時 :</th>
                <td class="panel-td" colspan="2"><span class="panel-span">${update}</span></td>
            </tr>
        </tbody>
    </table>
    ${cd.panelTextareaHtml( note )}`;
    
    return cd.panelCommon('Condcutor基本', html );
}
/*
##################################################
  Movementパネル
##################################################
*/
panelMovementHtml( nodeId ) {
    const cd = this;
    
    const node = cd.data[ nodeId ],
          id = fn.cv( node.movement_id, '', true ),
          name = fn.cv( node.movement_name, '', true ),
          note = fn.cv( node.note, '', true ),
          orchestrator = fn.cv( cd.getOrchestratorName( node.orchestra_id ), ''),
          operation = fn.cv( cd.getOperationName( node.operation_id ), ''),
          skip = ( node.skip_flag === '1')? ' checked': '';
          
    const html = `
    <table class="panel-table">
        <tbody>
            <tr>
                <th class="panel-th">Movement ID :</th>
                <td class="panel-td"><span id="movement-id" class="panel-span">${id}</span></td>
            </tr>
            <tr>
                <th class="panel-th">Orchestrator :</th>
                <td class="panel-td"><span id="movement-orchestrator" class="panel-span">${orchestrator}</span></td>
            </tr>
            <tr>
                <th class="panel-th">Name :</th>
                <td class="panel-td"><span id="movement-name" class="panel-span">${name}</span></td>
            </tr>
            <tr>
                <th class="panel-th">Default skip :</th>
                <td class="panel-td"><input id="movement-default-skip" class="panel-checkbox" type="checkbox"${skip}></td>
            </tr>
        </tbody>
    </table>
    <div class="panel-group">
        <div class="panel-group-title">Operation select</div>
        <table class="panel-table">
            <tbody>
                <tr>
                    <th class="panel-th">Operation :</th>
                    <td class="panel-td"><span id="movement-operation" class="panel-span" data-id="" data-value="">${operation}</span></td>
                </tr>
            </tbody>
        </table>
        <ul class="panel-button-group">
            <li class="panel-button-group-item"><button class="panel-button operation-select-button">Operation select</button></li>
            <li class="panel-button-group-item"><button class="panel-button operation-clear-button">Clear</button></li>
        </ul>
    </div>
    ${cd.panelTextareaHtml( note )}`;
    
    return cd.panelCommon('Movement', html );
}
/*
##################################################
  End nodeパネル
##################################################
*/
panelEndHtml( nodeId ) {
    const cd = this;
    
    const node = cd.data[ nodeId ],
          note = fn.cv( node.note, '', true ),
          end = node.end_type;
    
    // Radio選択HTML
    const html = [];
    
    const order = [ 5, 11, 7 ],
          orderLength = order.length;
    for ( let i = 0; i < orderLength; i++ ) {
        const name = cd.status.end[ order[i] ][ 0 ],
              title = cd.status.end[ order[i] ][ 1 ],
              endId = String( order[i] ),
              id = 'end-status-' + name,
              checked = ( end === endId )? ' checked': '';

        html.push(``
        + `<li class="end-status-select-item">`
          + `<input class="end-status-select-radio" type="radio" name="end-status" id="${id}" value="${endId}"${checked}>`
          + `<label class="end-status-select-label" for="${id}">${title}</label>`
        + `</li>`);
    }
    
    return cd.panelCommon('Conductor end', `
    <table class="panel-table">
        <tbody>
            <tr>
                <th class="panel-th">End status :</th>
                <td class="panel-td">
                    <div class="end-status-select">
                        <ul class="end-status-select-list">
                            ${html.join('')}
                        </ul>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
    ${cd.panelTextareaHtml( note )}`);
}
/*
##################################################
  分岐パネル
##################################################
*/
panelParallelBranchHtml( nodeId ) {
    const cd = this;
    
    const node = cd.data[ nodeId ],
          note = fn.cv( node.note, '', true );
          
    return cd.panelCommon('Parallel branch', `
    <table class="panel-table">
      <tbody>
          <tr>
              <th class="panel-th">Case :</th>
              <td class="panel-td">
                  <ul class="panel-button-group">
                      <li class="panel-button-group-item"><button class="branch-add panel-button">Add</button></li>
                      <li class="panel-button-group-item"><button class="branch-delete panel-button">Delete</button></li>
                  </ul>
              </td>
          </tr>
      </tbody>
      </table>
      ${cd.panelTextareaHtml( note )}`);
}
/*
##################################################
  マージパネル
##################################################
*/
panelMergeHtml( nodeId ) {
    const cd = this;
    
    const node = cd.data[ nodeId ],
          note = fn.cv( node.note, '', true );
    
    return cd.panelCommon('Parallel merge', `
    <table class="panel-table">
      <tbody>
        <tr>
          <th class="panel-th">Case :</th>
          <td class="panel-td">
            <ul class="panel-button-group">
              <li class="panel-button-group-item"><button class="branch-add panel-button">Add</button></li>
              <li class="panel-button-group-item"><button class="branch-delete panel-button">Delete</button></li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
    ${cd.panelTextareaHtml( note )}`);
    
}
/*
##################################################
  条件分岐パネル
##################################################
*/
panelConditionalBranchHtml( nodeId ) {
    const cd = this;
    
    const node = cd.data[ nodeId ],
          note = fn.cv( node.note, '', true );

    // 分岐をパネルに反映する
    const caseHtml = [],
          caseCount = Object.keys( node.terminal ).length - 1;
    let terminalConditionArray = []; // 使用中の分岐
    for( let terminalID in node.terminal ) {
        const terminalData = node.terminal[ terminalID ];
        if ( terminalData.type === 'out') {
            const caseNo = Number( terminalData.case ),
                  conditionLength = terminalData.condition.length,
                  conditionHTML = [];
                  console.log(caseCount)
                  console.log(caseNo)
            if ( caseCount !== caseNo ) {
                for ( let i = 0; i < conditionLength; i++ ) {
                  const condition = terminalData.condition[ i ];
                  terminalConditionArray.push( condition );
                  conditionHTML.push( cd.conditionBlockHTML( condition ) );
                }
                caseHtml[ caseNo - 1 ] = `<tr>`
                + `<th class="panel-th">Case${caseNo} :</th>`
                + `<td class="panel-td">`
                    + `<ul class="branch-case">${conditionHTML.join('')}</ul>`
                + `</td></tr>`;
            }
        }
    }
    
    // 未使用分岐をセット
    const nosetConditionHTML = [];
    for ( let key in cd.status.movement ){
        if ( key !== '9999' && terminalConditionArray.indexOf( key ) === -1 ) {
            nosetConditionHTML.push( cd.conditionBlockHTML( key ) );
        }
    }
          
    return cd.panelCommon('Conditional branch', `
    <table class="panel-table">
      <tbody>
        <tr>
          <th class="panel-th">Case :</th>
          <td class="panel-td">
            <ul class="panel-button-group">
              <li class="panel-button-group-item"><button class="branch-add panel-button">Add</button></li>
              <li class="panel-button-group-item"><button class="branch-delete panel-button">Delete</button></li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
    <hr class="panel-hr">
    <div id="branch-condition-move">
    <table id="branch-case-list" class="panel-table ">
      <tbody>
          ${caseHtml.join('')}
      </tbody>
    </table>
    <hr class="panel-hr">
    <table class="panel-table">
      <tbody>
        <tr>
          <th class="panel-th">Other :</th>
          <td class="panel-td">
              <ul id="noset-conditions" class="branch-case">
                  ${nosetConditionHTML.join('')}
              </ul>
          </td>
        </tr>
      </tbody>
    </table>
    </div>
    ${cd.panelTextareaHtml( note )}`);
}
/*
##################################################
  コールパネル
##################################################
*/
panelCallHtml( nodeId ) {
    const cd = this;
    
    const node = cd.data[ nodeId ],
          note = fn.cv( node.note, '', true );
          
    return cd.panelCommon('Condcutor call', `
    <table class="panel-table">
      <tbody>
        <tr>
          <th class="panel-th">Default skip :</th>
          <td class="panel-td"><input id="conductor-call-default-skip" class="panel-checkbox" type="checkbox"></td>
        </tr>
      </tbody>
    </table>
    <div class="panel-group">
      <div class="panel-group-title">Conductor select</div>
      <table class="panel-table">
        <tbody>
          <tr>
            <th class="panel-th">Conductor :</th>
            <td class="panel-td"><span id="conductor-call-name" class="panel-span" data-id="" data-value=""></span></td>
          </tr>
        </tbody>
      </table>
      <ul class="panel-button-group">
        <li class="panel-button-group-item"><button id="conductor-call-select" class="panel-button">Conductor select</button></li>
        <li class="panel-button-group-item"><button id="conductor-call-clear" class="panel-button">Clear</button></li>
      </ul>
    </div>
    <div class="panel-group">
      <div class="panel-group-title">Operation select</div>
      <table class="panel-table">
        <tbody>
          <tr>
            <th class="panel-th">Operation :</th>
            <td class="panel-td"><span class="panel-span" data-id="" data-value=""></span></td>
          </tr>
        </tbody>
      </table>
      <ul class="panel-button-group">
        <li class="panel-button-group-item"><button class="panel-button operation-select-button">Operation select</button></li>
        <li class="panel-button-group-item"><button class="panel-button operation-clear-button">Clear</button></li>
      </ul>
    </div>
    ${cd.panelTextareaHtml( note )}`);
}
/*
##################################################
  ステータス分岐パネル
##################################################
*/
panelStatusBranchHtml( nodeId ) {
    const cd = this;
    
    const node = cd.data[ nodeId ],
          note = fn.cv( node.note, '', true );
    
    const terminals = cd.data[ nodeId ].terminal;
    
    const outTerminals = Object.keys( terminals ).map(function( k ){
        return terminals[k];
    }).filter(function( v ){
        return ( v.case !== undefined && v.case !== 'else');
    }).sort(function( a, b ){
      if ( a.case > b.case ) {
        return 1;
      } else if ( a.case < b.case ) {
        return -1;
      } else {
        return 0;
      }
    });
              
    const terminalLength = outTerminals.length;
    let listHTML = '';
    for (let i = 0; i < terminalLength; i++ ) {
        const ifName = ( i === 0 )? 'if':'else if',
              value = ( outTerminals[i].condition !== undefined )? outTerminals[i].condition.join(' '): '';
        listHTML += ''
        + '<tr>'
          + '<th class="panel-th">' + ifName + ' :</th>'
          + '<td class="panel-td">';
        if ( cd.mode === 'execute' ) {
          listHTML +=  '<span class="panel-span">' + value + '</span>';
        } else {
          listHTML +=  '<input value="' + value + '" maxlength="256" class="status-file-input panel-text" type="text" data-terminal="' + outTerminals[i].id + '" title="">';
        }
        listHTML +=  '</td>'
        + '</tr>';
    }

return cd.panelCommon('Status file branch', `
  <table class="panel-table">
      <tbody>
          <tr>
              <th class="panel-th">Case :</th>
              <td class="panel-td">
                  <ul class="panel-button-group">
                      <li class="panel-button-group-item"><button class="branch-add panel-button">Add</button></li>
                      <li class="panel-button-group-item"><button class="branch-delete panel-button">Delete</button></li>
                  </ul>
              </td>
          </tr>
      </tbody>
  </table>
  <hr class="panel-hr">
  <div id="status-file-case-move">
    <table id="status-file-case-list" class="panel-table ">
        <tbody>
            ${listHTML}
        </tbody>
    </table>
  </div>
  ${cd.panelTextareaHtml( note )}`);
}
/*
##################################################
  整列パネル
##################################################
*/
panelAlignmentHtml() {
    return this.panelCommon('Node 整列', `
    <div class="panel-group">
      <div class="panel-group-title">整列</div>
      <ul class="panel-button-group">
        <li class="panel-button-group-item"><button id="node-align-left" class="panel-button node-align" title="水平方向左に整列"><span class="align-icon algin-left"></span></button></li>
        <li class="panel-button-group-item"><button id="node-align-vertical" class="panel-button node-align" title="水平方向中央に整列")}"><span class="align-icon algin-vertical"></span></button></li>
        <li class="panel-button-group-item"><button id="node-align-right" class="panel-button node-align" title="水平方向右に整列"><span class="align-icon algin-right"></span></button></li>
        <li class="panel-button-group-item"><button id="node-align-top" class="panel-button node-align" title="垂直方向上に整列"><span class="align-icon algin-top"></span></button></li>
        <li class="panel-button-group-item"><button id="node-align-horizonal" class="panel-button node-align" title="垂直方向中央に整列"><span class="align-icon algin-horizonal"></span></button></li>
        <li class="panel-button-group-item"><button id="node-align-bottom" class="panel-button node-align" title="垂直方向下に整列"><span class="align-icon algin-bottom"></span></button></li>
      </ul>
    </div>
    <div class="panel-group">
      <div class="panel-group-title">等間隔</div>
      <ul class="panel-button-group">
        <li class="panel-button-group-item"><button id="node-equally-spaced-vertical" class="panel-button node-equally-spaced" title="垂直方向等間隔に分布"><span class="align-icon algin-equally-vertical"></span></button></li>
        <li class="panel-button-group-item"><button id="node-equally-spaced-horizonal" class="panel-button node-equally-spaced" title="水平方向等間隔に分布"><span class="align-icon algin-equally-horizonal"></span></button></li>
      </ul>
    </div>`);
}
/*
##################################################
  共通パネル
##################################################
*/
panelCommonHtml( nodeId, title ) {
    const cd = this;
    
    const node = cd.data[ nodeId ],
          note = fn.cv( node.note, '', true );
          
    return cd.panelCommon( title, cd.panelTextareaHtml( note ) );
}
/*
##################################################
  Movementリスト
##################################################
*/
movementList() {
    const cd = this;
    
    // Movementリスト
    const $movementList = cd.$.panel.find('#movement-list'),
          $movementListRows = cd.$.panel.find('#movement-list-rows'),
          movementList = cd.info.list.movement,
          orchestraList = cd.info.list.orchestra;
    
    // Orchestratorリスト
    const $orchestraList = cd.$.panel.find('#orchestrator-list');
    
    const orchestraItem = [],
          orchestratorStyle = [];

    for ( const orchestra of orchestraList ) {
      $movementList.attr('data-orche' + orchestra.id, true );
      
      orchestraItem.push(``
      + `<li>`
          + `<label class="property-label">`
              + `<input type="checkbox" id="orchestra${orchestra.id}" name="filter-orchestra" checked>`
          + `</label>`
      + `</li>`);
      
      orchestratorStyle.push(`#movement-list[data-orche${orchestra.id}="false"]  .orche${orchestra.id}{display:none!important}`);

    }
    $movementList.prepend(`<style>${orchestratorStyle.join('')}</style>`);
    $orchestraList.html( orchestraItem.join('') );
    
    // Movementソート
    const sortMovementList = function( name, sort, type ) {
    
        movementList.sort( function( a, b ){
            if ( type === 'string') {
                const al = a[ name ].toLowerCase(),
                      bl = b[ name ].toLowerCase();
                if ( sort === 'desc') {
                    if( al < bl ) return 1;
                    if( al > bl ) return -1;
                } else if ( sort === 'asc') {
                    if( al > bl ) return 1;
                    if( al < bl ) return -1;
                }
            } else if ( type === 'number') {
                if ( sort === 'desc') {
                    return Number( b[ name ] ) - Number( a[ name ] );
                } else if ( sort === 'asc') {
                    return Number( a[ name ] ) - Number( b[ name ] );
                }
            }
        });
        
        const movementSortLost = [];
        for ( const movement of movementList ) {
            const orchestraName = movement.orchestra_name.toLocaleLowerCase().replace(/\s/g, '-');
            movementSortLost.push(``
            + `<tr class="orche${movement.orchestra_id}">`
                + `<th class="movement-list-orchestrator" title="${orchestraName}">`
                    + `<span class="add-node ${orchestraName}" data-id="${movement.id}"></span>`
                + `</th>`
                /*+ `<th class="movement-list-id"><div>${movement.id}</div></th>`*/
                + `<td class="movement-list-name"><div>${movement.name}</div></td>`
            + `</tr>`);
        }
        $movementListRows.html( movementSortLost.join('') );
        
        if ( $movementList.attr('data-filter') === 'name') {
            $movementFilter.trigger('input');
        } else {
            $movementIdFilter.trigger('input');
        }
    };
    
    // Movement Filter
    const $movementFilter = cd.$.panel.find('#movement-filter'),
          $movementIdFilter = cd.$.panel.find('#movement-filter-id');
    
    const movementFilter = function( inputValue, target ) {
        // スペースでsplit
        const valueArray = inputValue.split(/[\x20\u3000]+/),
              valueArrayLength = valueArray.length;

        // IDだった場合
        if ( target === '.movement-list-id') {
            for ( let i = 0; i < valueArrayLength; i++ ) {
                // 数値にならない場合消す
                if ( isNaN ( Number( valueArray[i] ) ) ) {
                    valueArray[i] = '';
                } else if ( valueArray[i] !== '') {
                    // 完全一致用
                    valueArray[i] = '^' + valueArray[i] + '$';
                }
            }
        }
        // or結合
        inputValue = valueArray.filter(function(v){return v !== '';}).join('|');

        const regExp = new RegExp( inputValue, "i");

        if ( inputValue !== '' ) {
            $movementList.find('.node-table tbody').find('tr').each( function(){
              const $tr = $( this ),
                    movementName = $tr.find( target ).text();
              if ( regExp.test( movementName ) ) {
                  $tr.removeClass('filter-hide');
              } else {
                  $tr.addClass('filter-hide');
              }
            });
        } else {
            $movementList.find('.filter-hide').removeClass('filter-hide');
        }
    };
    
    $movementFilter.on('input', function(){
        movementFilter( $( this ).val(), '.movement-list-name');
    });
    $movementIdFilter.on('input', function(){
        movementFilter( $( this ).val(), '.movement-list-id');
    });
    
    // ソート
    $movementList.find('.movement-list-sort').on('click', function(){
        const $sort = $( this ),
              sortTarget = $sort.attr('data-sort'),
              sortType = $sort.attr('data-sort-type'),
              sort = $sort.is('.asc')? 'desc': 'asc';
        $movementList.find('.asc, .desc').removeClass('asc desc');
        $sort.addClass( sort );
        sortMovementList( sortTarget, sort, sortType );
    });
    
    // デフォルトはID昇順
    $movementList.attr('data-filter', 'name');
    $movementList.find('.movement-list-id .movement-list-sort').addClass('asc');
    sortMovementList('id', 'asc', 'string');
    
    // Filter Setting画面
    const $filterSetting = cd.$.panel.find('#movement-filter-setting');
    
    // Filter設定オープン
    $movementList.find('.filter-setting-btn').on('click', function(){
        $filterSetting.show();
        // Text入力欄反映
        const inputType = $movementList.attr('data-filter');
        if ( inputType === 'name') {
             cd.$.panel.find('#filter-target-name').prop('checked', true );
        } else if ( inputType === 'id') {
             cd.$.panel.find('#filter-target-id').prop('checked', true );
        }
        // Orchestratorチェックボックスの反映
        for ( const orchestra of orchestraList ) {
            const flag = ( $movementList.attr('data-orche' + orchestra.id ) === 'true' )? true: false;
            cd.$.panel.find('#orchestra' + orchestra.id ).prop('checked', flag );
        }
    });
    
    // Filter設定キャンセル
    cd.$.panel.find('#movement-filter-cancel').on('click', function(){
        $filterSetting.hide();
    });
    
    // Filter設定決定
    cd.$.panel.find('#movement-filter-ok').on('click', function(){
        const inputType = $filterSetting.find('[name="filter-target"]:checked').attr('id');
        if ( inputType === 'filter-target-name') {
            $movementList.attr('data-filter', 'name');
            $movementFilter.trigger('input');
        } else if ( inputType === 'filter-target-id') {
            $movementList.attr('data-filter', 'id');
            $movementIdFilter.trigger('input');
        }
        for ( const orchestra of orchestraList ) {
            $movementList.attr('data-orche' + orchestra.id, $('#orchestra' + orchestra.id ).prop('checked') );
        }
        $filterSetting.hide();
    });
}
/*
##################################################
  Functionリスト
##################################################
*/
functionList() {

}
/*
##################################################
  パネルをnodeIDのものに変更する
##################################################
*/
panelChange( nodeID ) {
  const cd = this;

  // 複数選択されている場合は整列パネルを表示する
  if ( cd.select.length <= 1 ) {
      let panelType = '';
      
      // nodeIDが未定義の場合はコンダクターパネルを表示
      if ( nodeID === undefined ) {
          panelType = 'conductor';
      } else if ( cd.mode === 'checking') {
          // 作業確認の場合はすべてNodeとする
          panelType = 'node';
      } else {
          panelType = cd.data[ nodeID ].type;
      }
      cd.setPanel( panelType, nodeID );
  } else {
      cd.setPanel('alignment');
  }

    /*

    
    // パネルごとの処理
    switch( panelType ) {
      case 'movement': {
          $('#movement-id').text( cd.data[ nodeID ].movement_id );
          $('#movement-orchestrator').text( cd.info.dict.orchestra[ cd.data[ nodeID ].orchestra_id ] );
          $('#movement-name').text( cd.data[ nodeID ].movement_name );
          panelOperation('#movement-operation');          
          // Skip
          const nodeChecked = ( Number( cd.data[ nodeID ].skip_flag ) === 1 ) ? true : false;
          $('#movement-default-skip').prop('checked', nodeChecked );
        }
        break;
      case 'call': {
          let callConductor = cd.data[ nodeID ].call_conductor_id;
          if ( callConductor !== undefined && callConductor !== null ) {
            const conductorName = cd.info.dict.conductor[ callConductor ];
            callConductor = '[' + callConductor + ']:' + conductorName;
          } else {
            callConductor = '';
          }
          $('#conductor-call-name').text( callConductor );
          panelOperation('#conductor-call-operation');
          // Skip
          const nodeChecked = ( Number( cd.data[ nodeID ].skip_flag ) === 1 ) ? true : false;
          $('#conductor-call-default-skip').prop('checked', nodeChecked );
        }

      case 'node': {
        // パネル情報更新
        const nodeInfo = cd.status.conductor['node_info'][ nodeID ];
        const panelNodeInfo = [
          ['#node-type', cd.data[ nodeID ].type ],
          ['#node-instance-id', nodeInfo.NODE_INSTANCE_NO ],
          ['#node-name', nodeInfo.NODE_NAME ],
          ['#node-status', cd.status.node[ nodeInfo.STATUS ][1] ],
          ['#node-status-file', nodeInfo.STATUS_FILE ],
          ['#node-start', nodeInfo.TIME_START ],
          ['#node-end', nodeInfo.TIME_END ],
          ['#node-oepration-id', nodeInfo.OPERATION_ID ],
          ['#node-operation-name', nodeInfo.OPERATION_NAME ]
        ];

        const panelNodeInfoLength = panelNodeInfo.length;

        for ( let i = 0; i < panelNodeInfoLength; i++ ) {
          if ( panelNodeInfo[ i ][ 1 ] === null || panelNodeInfo[ i ][ 1 ] === undefined ) panelNodeInfo[ i ][ 1 ] = '';
          $( panelNodeInfo[ i ][ 0 ] ).text( panelNodeInfo[ i ][ 1 ] );
        }
        // Jump
        if ( 'JUMP' in nodeInfo ) {
          const jumpURL = nodeInfo.JUMP;
          $('#node-Jump').html('<a href="' + jumpURL + '" target="_blank">ジャンプ</a>');
        } else {
          $('#node-Jump').empty();
        }
        break;
      }
      default:
    }

  }
  */
}
/*
##################################################
  数値比較
##################################################
*/
numberCompare( a, b, mode ) {
    if ( a === null && b === null ) return false;
    a = ( a === null )? b: a;
    b = ( b === null )? a: b;
    if ( mode === 's') {
        return ( a < b )? a: b;
    } else {
        return ( a < b )? b: a;
    }
}
/*
##################################################
  整列
##################################################
*/
nodeAlignment() {
    const cd = this;
    
    cd.$.conductorParameter.on('click', '.panel-button.node-align', function() {
      const alignType = $( this ).attr('id').replace('node-align-',''),
            selectLength = cd.select.length;

      let pointX1 = null,
          pointY1 = null,
          pointX2 = null,
          pointY2 = null;

      // 取り消し、やり直し用の移動前移動後の座標を入れる
      const nodePosition = {
        'before': {},
        'after': {}
      };

      // 基準になる位置を求める
      for ( let i = 0; i < selectLength; i++) {
        const nodeID = cd.select[i],
              x = cd.data[nodeID].x,
              y = cd.data[nodeID].y,
              w = cd.data[nodeID].w,
              h = cd.data[nodeID].h;
        nodePosition['before'][nodeID] = {
          'x': x,
          'y': y
        };
        switch( alignType ) {
          case 'left':
            pointX1 = cd.numberCompare( pointX1, x, 's');
            break;
          case 'vertical':
            pointX1 = cd.numberCompare( pointX1, x, 's');
            pointX2 = cd.numberCompare( pointX2, x + w );
            break;
          case 'right':
            pointX1 = cd.numberCompare( pointX1, x + w );
            break;
          case 'top':
            pointY1 = cd.numberCompare( pointY1, y, 's');
            break;
          case 'horizonal':
            pointY1 = cd.numberCompare( pointY1, y, 's');
            pointY2 = cd.numberCompare( pointY2, y + h );
            break;
          case 'bottom':
            pointY1 = cd.numberCompare( pointY1, y + h );
            break;
        }
      }

      // 整列する
      for ( let i = 0; i < selectLength; i++ ) {
        const nodeID = cd.select[i],
              x = cd.data[nodeID].x,
              y = cd.data[nodeID].y,
              w = cd.data[nodeID].w,
              h = cd.data[nodeID].h;
        let nx, ny;
        switch( alignType ) {
          case 'left':
            nx = pointX1;
            ny = y;
            break;
          case 'vertical':
            nx = pointX1 + (( pointX2 - pointX1 ) / 2 ) - ( w / 2 );
            ny = y;
            break;
          case 'right':
            nx = pointX1 - w;
            ny = y;
            break;
          case 'top':
            nx = x;
            ny = pointY1;
            break;
          case 'horizonal':
            nx = x;
            ny = pointY1 + (( pointY2 - pointY1 ) / 2 ) - ( h / 2 );
            break;
          case 'bottom':
            nx = x;
            ny = pointY1 - h;
            break;
        }
        cd.nodeMoveSet( nodeID, nx, ny );
        nodePosition['after'][nodeID] = {
          'x': nx,
          'y': ny
        }
      }

      cd.conductorHistory().align( nodePosition );
      cd.updateConductorData();

    });

    // 選択されたノードを等間隔に分布する
    cd.$.conductorParameter.on('click', '.panel-button.node-equally-spaced', function() {
      const alignType = $( this ).attr('id').replace('node-equally-spaced-',''),
            selectLength = cd.select.length;

      // 取り消し、やり直し用の移動前移動後の座標を入れる
      const nodePosition = {
        'before': {},
        'after': {}
      };

      // 縦か横か？
      const dXY = ( alignType === 'vertical')? 'y': 'x',
            dWH = ( alignType === 'vertical')? 'h': 'w';

      // 選択されているノードが2以下の場合は何もしない
      if ( cd.select < 3 ) return false;

      // Node
      const nodeArray = new Array( selectLength );
      for ( let i = 0; i < selectLength; i++ ) {
        const nodeID = cd.select[i];
        nodeArray[i] = {
          'id': nodeID,
          'x': cd.data[nodeID].x,
          'y': cd.data[nodeID].y,
          'h': cd.data[nodeID].h,
          'w': cd.data[nodeID].w
        };
        nodePosition['before'][nodeID] = {
          'x': cd.data[nodeID].x,
          'y': cd.data[nodeID].y
        };
      }

      // 一番下のノードを調べる
      nodeArray.sort( function( a, b ){
        if ( a[dXY] + a[dWH] < b[dXY] + b[dWH] ) return -1;
        if ( a[dXY] + a[dWH] > b[dXY] + b[dWH] ) return 1;
        return 0;
      });
      let s2 = nodeArray[ selectLength - 1 ][dXY];

      // 一番上のノードを調べる
      nodeArray.sort( function( a, b ){
        if ( a[dXY] < b[dXY] ) return -1;
        if ( a[dXY] > b[dXY] ) return 1;
        return 0;
      });
      let s1 = nodeArray[ 0 ][dXY] + nodeArray[ 0 ][dWH];

      let positionRange = ( s2 - s1 > 0 )? s2 - s1: 0;

    // 分布範囲がノードの大きさより小さいかどうか
      let nodeWidth = 0;
      for ( let i = 1; i < selectLength - 1; i++ ) {
        nodeWidth += cd.data[nodeArray[i].id][dWH];
      }
      if ( nodeWidth < positionRange ) {
        const equallySpaceWidth = Math.round(( positionRange - nodeWidth ) / ( selectLength - 1 ));
        let equallySpaceSum = s1 + equallySpaceWidth;
        for ( let i = 1; i < selectLength - 1; i++ ) {
          const x = ( alignType === 'vertical')? nodeArray[i].x: equallySpaceSum,
                y = ( alignType === 'vertical')? equallySpaceSum: nodeArray[i].y;
          cd.nodeMoveSet( nodeArray[i].id, x, y );
          nodePosition['after'][nodeArray[i].id] = {
            'x': x,
            'y': y
          }
          equallySpaceSum += nodeArray[i][dWH] + equallySpaceWidth;
        }
      } else {
        // 分布範囲がノードサイズより小さい場合はノードのセンターで分布する
        s1 = s1 - ( nodeArray[0][dWH] / 2 );
        s2 = s2 + ( nodeArray[ selectLength - 1 ][dWH] / 2 );
        positionRange = ( s2 - s1 > 0 )? s2 - s1: 0;
        const equallySpaceWidth = Math.round( positionRange / ( selectLength - 1 ));
        let equallySpaceSum = s1 + equallySpaceWidth;
        for ( let i = 1; i < selectLength - 1; i++ ) {
          const x = ( alignType === 'vertical')? nodeArray[i].x: equallySpaceSum - ( nodeArray[i].w / 2 ),
                y = ( alignType === 'vertical')? equallySpaceSum - ( nodeArray[i].h / 2 ): nodeArray[i].y;
          cd.nodeMoveSet( nodeArray[i].id, x, y );
          nodePosition['after'][nodeArray[i].id] = {
            'x': x,
            'y': y
          }
          equallySpaceSum += equallySpaceWidth;
        }
      }

      cd.conductorHistory().align( nodePosition );
      cd.updateConductorData();

    });
}
/*
##################################################
  条件ブロック
##################################################
*/
conditionBlockHTML( key ) {
  const  movementEndStatus = this.status.movement;
  return '<li class="' + movementEndStatus[ key ][0] + ' branch-case-Item" data-end-status="' + key + '">' + movementEndStatus[ key ][1] + '</li>';
}
/*
##################################################
  条件状態更新
##################################################
*/
conditionUpdate( nodeID ) {
  const cd = this;
  
  $('#branch-case-list').find('tbody').find('.branch-case').each( function( i ) {
      let conditions = [],
          tergetTerminalID = '';
      $( this ).find('li').each( function(){
          conditions.push( $( this ).attr('data-end-status') );
      });
      // どこの条件か？
      for ( let terminalID in cd.data[ nodeID ].terminal ) {
        const terminal = cd.data[ nodeID ].terminal[ terminalID ];
        if ( terminal.case === i + 1 ) {
          tergetTerminalID = terminal.id;
        }
      }
      // 条件を追加
      const conditionLength = conditions.length;
      let terminalConditionHTML = '';
      for ( let i = 0; i < conditionLength; i++ ) {
        terminalConditionHTML += cd.conditionBlockHTML( conditions[ i ] );
      }
      $('#' + tergetTerminalID ).prev('.node-body').find('ul').html( terminalConditionHTML );
    });

    cd.branchLine( nodeID );

    const beforeNodeData = $.extend( true, {}, cd.data[ nodeID ] );
    cd.nodeSet( $('#' + nodeID ) );
    const afterNodeData = $.extend( true, {}, cd.data[ nodeID ] );
    cd.conductorHistory().branch( beforeNodeData, afterNodeData );

    cd.connectEdgeUpdate( nodeID );
}
/*
##################################################
  Skipチェックボックス状態変更
##################################################
*/
nodeCheckStatus( nodeID ) {
  const cd = this;
        
  const $node = $('#' + nodeID ),
        $checkbox = $node.find('.node-skip-checkbox'),
        checkFlag = $checkbox.prop('checked');
  if ( checkFlag ) {
      $node.removeClass('skip');
      $checkbox.prop('checked', false );
      cd.data[ nodeID ].skip_flag = '0';
  } else {
      $checkbox.prop('checked', true );
      $node.addClass('skip');
      cd.data[ nodeID ].skip_flag = '1';
  }
}
/*
##################################################
  個別オペレーションセレクト
##################################################
*/
operationUpdate( nodeID, id, name ) {
    const cd = this;

    const $node = $('#' + nodeID );
    if ( id !== 0 ) { 
      $node.addClass('operation');
      cd.data[ nodeID ].OPERATION_NO_IDBH = id;
      $node.find('.node-operation-data').text('[' + id + ']:' + name );
    } else {
      $node.removeClass('operation');
      cd.data[ nodeID ].OPERATION_NO_IDBH = null;
      $node.find('.node-operation-data').text('');
    }
    cd.panelChange( nodeID );
}
/*
##################################################
  Callコンダクターセレクト
##################################################
*/
callConductorUpdate( nodeID, id, name ) {
    const cd = this;
          
    const $node = $('#' + nodeID );
    if ( id !== 0 ) { 
      cd.data[ nodeID ].CALL_CONDUCTOR_ID = id;
      $node.addClass('call-select').find('.select-conductor-name-inner').text('[' + id + ']:' + name );
    } else {
      cd.data[ nodeID ].CALL_CONDUCTOR_ID = null;
      $node.removeClass('call-select').find('.select-conductor-name-inner').text('Not selected');
    }
    cd.nodeSet( $('#' + nodeID ) );
    cd.connectEdgeUpdate( nodeID );
    cd.panelChange( nodeID );
}
/*
##################################################
  モーダル用リスト
##################################################
*/
modalSelectList( type ) {
  const cd = this;
  
  const $modalBody = $('.editor-modal-body');
  let operationListHTML = ''
  + '<div class="modal-table-wrap">'
    + '<table class="modal-table modal-select-table">'
      + '<thead>'
        + '<th class="id">ID</th><th class="name">Name</th>'
      + '</thead>'
      + '<tbody>'
        + '<tr data-id="0" data-name="unselected" class="selected"><th>-</th><td>Unselected</td></tr>';
  if ( type === 'operation') {
    operationListHTML += cd.modalTr( cd.info.list.operation, 'operation_id','operation_name')
  } else if ( type === 'conductor') {
    operationListHTML += cd.modalTr( cd.info.list.conductor, 'conductor_id','conductor_name')
  }
  operationListHTML += ''
      + '</tbody>'
    + '</table>'
  + '</div>';
  
  $modalBody.html( operationListHTML );
  
  // 選択
  $modalBody.find('.modal-select-table').on('click', 'tr', function(){
      const $tr = $( this );
      $modalBody.find('tbody').find('.selected').removeClass('selected');
      $tr.addClass('selected');
  });
  
  // 決定・取り消しボタン
  const $modalButton = $('.editor-modal-footer-menu-button');
  $modalButton.prop('disabled', false ).on('click', function() {
    const $button = $( this ),
          btnType = $button.attr('data-button-type');
    switch( btnType ) {
      case 'ok': {
        const nodeID = cd.select[0],
              $selectTr = $modalBody.find('tbody').find('.selected'),
              dataID = Number( $selectTr.attr('data-id') ),
              dataName = $selectTr.attr('data-name');
        if ( type === 'operation') {
          cd.operationUpdate( nodeID, dataID, dataName );
        } else if ( type === 'conductor') {
          cd.callConductorUpdate( nodeID, dataID, dataName );
        }
        //editor.modalClose();
      } break;
      case 'cancel':
        //editor.modalClose();
        break;
    }
  }); 
}
/*
##################################################
  パネルイベント
##################################################
*/
panelEvents() {
    const cd = this;
    
    // オペレーション選択モーダル
    const config = {
        mode: 'modeless',
        header: {
            title: 'オペレーション選択',
            move: false,
            close: false
        }
    };
    const operationModal = new Dialog( config );
    
    // Conductor name
    cd.$.conductorParameter.on('input', '#conductor-class-name', function() {
        cd.data['conductor'].conductor_name = $( this ).val();
    });

    // 分岐パネル
    cd.$.conductorParameter.on('click', '.branch-add', function(){
        cd.addBranch( cd.select[ 0 ] );
    });
    cd.$.conductorParameter.on('click', '.branch-delete', function(){
        cd.removeBranch( cd.select[ 0 ] );
    });

    // Skipチェックボックス
    cd.$.conductorParameter.on('change', '.panel-checkbox', function() {
        if ( cd.select.length === 1 ) {
            cd.nodeCheckStatus( cd.select[0] );
        }
    });
    
    // 条件移動
    cd.$.conductorParameter.on('mousedown', '.branch-case-Item', function( e ) {
        const $condition = $( this ),
              scrollTop = cd.$.window.scrollTop(),
              scrollLeft = cd.$.window.scrollLeft(),
              conditionWidth = $condition.outerWidth(),
              conditionHeight = $condition.outerHeight(),
              mousedownPositionX = e.pageX,
              mousedownPositionY = e.pageY;

        let moveX, moveY;

        cd.setAction('case-drag');

        cd.$.conductorParameter.find('.branch-case').on({
          'mouseenter' : function() { $( this ).addClass('hover'); },
          'mouseleave' : function() { $( this ).removeClass('hover'); }
        })

        $condition.css({
          'pointer-events' : 'none',
          'display' : 'block',
          'position' : 'fixed',
          'left' : ( mousedownPositionX - scrollLeft - conditionWidth / 2 ) + 'px',
          'top' : ( mousedownPositionY - scrollTop - conditionHeight / 2 ) + 'px',
          'z-index' : 99999
        });

        cd.$.window.on({
          'mousemove.conditionMove' : function( e ) {
            moveX = e.pageX - mousedownPositionX;
            moveY = e.pageY - mousedownPositionY;
            $condition.css('transform', 'translate(' + moveX + 'px,' + moveY + 'px)');
          },
          'mouseup.conditionMove' : function() {
            $condition.removeAttr('style');
            cd.$.window.off('mousemove.conditionMove mouseup.conditionMove');
            cd.clearAction();
            if ( cd.$.conductorParameter.find('.branch-case.hover').length ) {
              cd.$.conductorParameter.find('.branch-case.hover').append( $condition );
              cd.$.conductorParameter.find('.branch-case').off().removeClass('hover');
              // 条件反映
              cd.conditionUpdate( cd.select[0] );
            }
          }
        });
    });

    // Status file 条件値入力
    cd.$.conductorParameter.on('input', '.status-file-input', function() {
        const $input = $( this ),
              terminalID = $input.attr('data-terminal'),
              val = $input.val(),      
              $terminal = $('#' + terminalID );

        // 値をセット
        if ( cd.data[ cd.select[0] ].type === 'status-file-branch') {
          cd.data[ cd.select[0] ].terminal[terminalID].condition = [val];
          $terminal.prev('.node-body').find('.branch-if-value-inner').text( val );
        }
    });

    // Note更新
    cd.$.conductorParameter.on('input', '.panel-textarea', function() {

        if ( cd.select.length === 1 ) {
            const $targetNodeNote = $('#' + cd.select[0] ).find('.node-note');
            let noteText = $( this ).val();

            // 入力されたテキスト
            cd.data[ cd.select[0] ].note = noteText;

            // タグの無害化
            noteText = fn.escape( noteText, true );

            if ( noteText === '' ) {
                $targetNodeNote.removeClass('note-open');
            } else {
                $targetNodeNote.addClass('note-open').find('p').html( noteText );
            }
        } else if ( cd.select.length === 0 ) {
            cd.data['conductor'].note = $( this ).val();
        }

    });
    
    // Conductor End 終了ステータス選択
    cd.$.conductorParameter.on('change', '.end-status-select-radio', function(){
        // 選択されているノードが一つかどうか
        if ( cd.select.length <= 1 ) {
          const nodeID = cd.select[0],
                $node = $('#' + nodeID ),
                val = $( this ).val(),
                nodeName = ( val === '5')? 'End': 'End : ' + cd.status.end[ val ][ 1 ];
          $node.attr('data-end-status', cd.status.end[ val ][ 0 ] )
            .find('.node-name > span').text( nodeName );
          
          cd.data[ nodeID ].end_type = $( this ).val();

          // サイズを更新
          cd.nodeSet( $node );
        }
    });
    
    // Operation選択
    cd.$.conductorParameter.on('click', '.operation-select-button', function(){
        operationModal.open('');
    });    
    
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   取り消し、やり直し
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

/*
##################################################
  取り消し、やり直し初期設定
##################################################
*/
initHistory() {
    const cd = this;
    
    cd.history = {
        max: 10, // 最大履歴数
        counter: 0,
        list: [],
        interrupt: []
    };
    
    cd.historyButtonCheck();
}
/*
##################################################
  取り消し、やり直しボタンチェック
##################################################
*/
historyButtonCheck() {
    const cd = this;
    
    const $undoButton = cd.$.header.find('.editor-menu-button[data-menu="undo"]'),
          $redoButton = cd.$.header.find('.editor-menu-button[data-menu="redo"]');
    
    if ( cd.history.list[ cd.history.counter - 1 ] !== undefined ) {
      $undoButton.prop('disabled', false );
    } else {
      $undoButton.prop('disabled', true );
    }
    
    if ( cd.history.list[ cd.history.counter ] !== undefined ) {
      $redoButton.prop('disabled', false );
    } else {
      $redoButton.prop('disabled', true );
    }
}
/*
##################################################
  履歴数の調整
##################################################
*/
historyControl() {
    const cd = this;
    
    // 履歴追加後の履歴を削除する
    if ( cd.history.list[ cd.history.counter ] !== undefined ) {
      cd.history.list.length = cd.history.counter;
    } 
    // 最大履歴数を超えた場合最初の履歴を削除する
    if ( cd.history.list.length > cd.history.max ) {
      cd.history.list.shift();
      cd.history.counter--;
    }
    cd.historyButtonCheck();
}
/*
##################################################
  結線割込みやり直し
##################################################
*/
interruptRedo( interruptData ) {
  const cd = this;
  
  cd.removeEdge( interruptData[0].id, 0 );
  cd.data[ interruptData[1].id ] = interruptData[1];
  cd.edgeConnect( interruptData[1].id );
  cd.data[ interruptData[2].id ] = interruptData[2];
  cd.edgeConnect( interruptData[2].id );
}
/*
##################################################
  分岐線やり直し
##################################################
*/
branchUndoRedo( nodeID, nodeData ) {
  const cd = this;
        
  $('#' + nodeID ).remove();
  delete cd.data[ nodeID ];
  cd.data[ nodeID ] = nodeData;
  const $branchNode = cd.createNode( nodeID );
  
  cd.$.artBoard.append( $branchNode );
  cd.nodeSet( $branchNode, cd.data[ nodeID ].x, cd.data[ nodeID ].y );
  cd.branchLine( nodeID );
  // 接続チェック
  for ( let terminalID in cd.data[ nodeID ]['terminal'] ) {
    if ( 'edge' in cd.data[ nodeID ]['terminal'][ terminalID ] ) {
      $branchNode.find('#' + terminalID ).addClass('connected');
    }
  }
  
  cd.connectEdgeUpdate( nodeID );
}
/*
##################################################
  履歴管理
##################################################
*/
conductorHistory() {
    const cd = this;
        
    return {
        // 割り込んだ際にEdgeを保存しておく
        'interrupt': function( removeEdgeData, newEdge1, newEdge2 ) {
          const newEdge1Data = $.extend( true, {}, cd.data[ newEdge1 ] ),
                newEdge2Data = $.extend( true, {}, cd.data[ newEdge2 ] );
          cd.history.interrupt = [ removeEdgeData, newEdge1Data, newEdge2Data ];
        },
        // リストからノードセット
        'nodeSet': function( nodeID, interruptFlag ) {
          const nodeDataCopy = $.extend( true, {}, cd.data[ nodeID ] );
          if ( interruptFlag === false ) {
            cd.history.interrupt = [];
          }
          cd.history.list[ cd.history.counter++ ] = {
            'type': 'nodeSet',
            'data': {
              'interruptFlag': interruptFlag,
              'nodeData': nodeDataCopy,
              'interrupt': cd.history.interrupt
            }
          };

          cd.historyControl();
        },
        // 移動
        'move': function( nodeID, x, y, interruptFlag ) {
          if ( interruptFlag === false ) {
            cd.history.interrupt = [];
          }
          cd.history.list[ cd.history.counter++ ] = {
            'type': 'move',
            'data': {
              'interruptFlag': interruptFlag,
              'nodeID': nodeID,
              'x': x,
              'y': y,
              'interrupt': cd.history.interrupt
            }
          };
          cd.historyControl();
        },
        // 整列
        'align': function( position ) {
          const wc = cd.history.counter++;
          cd.history.list[ wc ] = {
            'type': 'align',
            'data': position
          };
          cd.historyControl();
        },
        // 分岐の増減など
        'branch': function( beforeNodeData, afterNodeData ) {
          if (
              cd.history.list[ cd.history.counter - 1 ] !== undefined &&
              cd.history.list[ cd.history.counter - 1 ].type === 'branch' &&
              cd.history.list[ cd.history.counter - 1 ]['data'].nodeID === afterNodeData.id
          ) {
            cd.history.counter--;
            cd.history.list[ cd.history.counter++ ]['data'].afterNodeData = afterNodeData;
          } else {
            cd.history.list[ cd.history.counter++ ] = {
              'type': 'branch',
              'data': {
                'nodeID': afterNodeData.id,
                'beforeNodeData': beforeNodeData,
                'afterNodeData': afterNodeData
              }
            };
          }
          cd.historyControl(); 
        },
        // Edge接続
        'connect': function( edgeID ) {
          const edgeDataCopy = $.extend( true, {}, cd.data[ edgeID ] );
          cd.history.list[ cd.history.counter++ ] = {
            'type': 'connect',
            'data': {
              'edgeID': edgeID,
              'edgeData': edgeDataCopy
            }
          };
          cd.historyControl();
        },
        // Nodeを削除
        'nodeRemove': function( nodeID ) {
          let nodeIdCopy;
          if ( Array.isArray( nodeID ) ) {
            nodeIdCopy = $.extend( true, [], nodeID );
          } else {
            nodeIdCopy = [ nodeID ];
          }        
          // 接続している線の一覧を作成
          let connectEdgeList = [];
          const nodeIdLength = nodeIdCopy.length;
          for ( let i = 0; i < nodeIdLength; i++ ) {
            if ( 'terminal' in  cd.data[ nodeIdCopy[i] ] ) {
              const terminals = cd.data[ nodeIdCopy[i] ].terminal;
              for ( let terminal in terminals ) {
                const terminalData = terminals[ terminal ];
                if ( 'edge' in terminalData ) {
                  if ( connectEdgeList.indexOf( terminalData.edge ) === -1 ) {
                    connectEdgeList.push( terminalData.edge );
                  }
                }
              }
            }
          }    
          // 削除するnode, edgeをコピーする
          const removeConductorList = nodeIdCopy.concat( connectEdgeList ),
                removeConductorLength = removeConductorList.length;
          let removeConductorData = {}
          for ( let i = 0; i < removeConductorLength; i++ ) {
            removeConductorData[ removeConductorList[i] ] = $.extend( true, {}, cd.data[ removeConductorList[i] ] );
          }    
          cd.history.list[ cd.history.counter++ ] = {
            'type': 'nodeRemove',
            'data': {
              'removeData': removeConductorData,
              'removeNodeIdList': nodeIdCopy
            }
          };
          cd.historyControl();
        },
        // Edgeを削除
        'edgeRemove': function( edgeID ) {
          const edgeDataCopy = $.extend( true, {}, cd.data[ edgeID ] );
          cd.history.list[ cd.history.counter++ ] = {
            'type': 'edgeRemove',
            'data': {
              'removeEdgeID': edgeID,
              'removeEdgeData': edgeDataCopy
            }
          };
          cd.historyControl();
        },
        'undo': function() {
          if ( cd.history.list[ cd.history.counter - 1 ] !== undefined ) {
            cd.history.counter--;
            const undo = cd.history.list[ cd.history.counter ];
            cd.nodeDeselect();
            cd.panelChange();

            switch( undo['type'] ) {
              case 'nodeSet':
                cd.nodeRemove( undo['data']['nodeData'].id );
                if ( undo['data']['interruptFlag'] === true ) {
                  cd.data[ undo['data']['interrupt'][0].id ] = undo['data']['interrupt'][0];
                  cd.edgeConnect( undo['data']['interrupt'][0].id );
                }
                break;
              case 'branch':
                cd.branchUndoRedo( undo['data'].nodeID, undo['data'].beforeNodeData );
                break;
              case 'move':
                cd.nodeMoveSet( undo['data']['nodeID'], -undo['data']['x'], -undo['data']['y'], 'relative');
                if ( undo['data']['interruptFlag'] === true ) {
                  cd.removeEdge( undo['data']['interrupt'][1].id, 0 );
                  cd.removeEdge( undo['data']['interrupt'][2].id, 0 );
                  cd.cd.data[ undo['data']['interrupt'][0].id ] = undo['data']['interrupt'][0];
                  cd.edgeConnect( undo['data']['interrupt'][0].id );
                }
                break;
              case 'align':
                for ( const id in undo['data']['before'] ) {
                  cd.nodeMoveSet( id, undo['data']['before'][id].x, undo['data']['before'][id].y );
                }
                break;
              case 'connect':
                cd.removeEdge( undo['data']['edgeID'], 0 );
                break;
              case 'nodeRemove':
                $.extend( cd.data, undo['data']['removeData'] );
                cd.nodeReSet( undo['data']['removeData'] );
                break;
              case 'edgeRemove':
                cd.data[ undo['data']['removeEdgeID'] ] = undo['data']['removeEdgeData'];
                cd.edgeConnect( undo['data']['removeEdgeID'] );
                break;
            }  

            cd.historyButtonCheck();
          }
        },
        'redo': function() {
          if ( cd.history.list[ cd.history.counter ] !== undefined ) {
            const redo = cd.history.list[ cd.history.counter++ ];
            cd.nodeDeselect();
            cd.panelChange();

            switch( redo['type'] ) {
              case 'nodeSet': {
                  const nodeID = redo['data']['nodeData'].id;
                  cd.data[ nodeID ] = redo['data']['nodeData'];

                  const $node = cd.createNode( nodeID );
                  cd.$.artBoard.append( $node );
                  cd.nodeSet( $node, cd.data[ nodeID ].x, cd.data[ nodeID ].y );

                  const nodeCheck = ['merge', 'conditional-branch', 'parallel-branch', 'status-file-branch'];
                  if ( nodeCheck.indexOf( cd.data[ nodeID ].type ) !== -1 ) {
                    $node.ready( function(){
                      cd.branchLine( nodeID );
                    });
                  }
                  if ( redo['data']['interruptFlag'] === true ) {
                    cd.interruptRedo( redo['data']['interrupt'] );
                  }
              } break;
              case 'branch':
                cd.branchUndoRedo( redo['data'].nodeID, redo['data'].afterNodeData );
                break;
              case 'move':
                cd.nodeMoveSet( redo['data']['nodeID'], redo['data']['x'], redo['data']['y'], 'relative');
                if ( redo['data']['interruptFlag'] === true ) {
                  cd.interruptRedo( redo['data']['interrupt'] );
                }
                break;
              case 'align':
                for ( const id in redo['data']['after'] ) {
                  cd.nodeMoveSet( id, redo['data']['after'][id].x, redo['data']['after'][id].y );
                }
                break;
              case 'connect':
                cd.data[ redo['data']['edgeID'] ] = redo['data']['edgeData'];
                cd.edgeConnect( redo['data']['edgeID'] );
                break;
              case 'nodeRemove':
                cd.nodeRemove( redo['data']['removeNodeIdList'] );
                break;
              case 'edgeRemove':
                cd.removeEdge( redo['data']['removeEdgeID'], 0 );
                break;
            }

            cd.historyButtonCheck();  
          }
        },
        'clear': function() {
            cd.history.counter = 0;
            cd.history.list = [];

            cd.historyButtonCheck();
        }
    };
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   選択用モーダル
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

/*
##################################################
  コンダクター選択
##################################################
*/
selectConductorModalOpen() {
    const cd = this;
    return new Promise(function( resolve, reject ){
        const setClickEvent = function() {
            const button = '.tableHeaderMainMenuButton[data-type="tableSelect"],.tableHeaderMainMenuButton[data-type="tableCancel"]';
            cd.selectConductorModal.table.$.header.one('click', button, function(){
                cd.selectConductorModal.modal.hide();
                
                const $button = $( this ),
                      type = $button.attr('data-type');
                switch ( type ) {
                    case 'tableSelect': {
                        const selectId = cd.selectConductorModal.table.select.select;
                        resolve( selectId );
                    } break;
                    case 'tableCancel':
                        cd.selectConductorModal.modal.hide();
                        resolve( null );
                    break;
                }
            });
        };
        
        if ( !cd.selectConductorModal ) {
            fn.initSelectModal('Conductor選択', 'conductor_class_list').then(function( modal ){
                cd.selectConductorModal = modal;
                setClickEvent();
            });
        } else {
            cd.selectConductorModal.modal.show();
            setClickEvent();
        }
    });
}

/*
##################################################
  オペレーション選択
##################################################
*/
selectOperationModalOpen() {
    const cd = this;
    return new Promise(function( resolve, reject ){
        const setClickEvent = function() {
            const button = '.tableHeaderMainMenuButton[data-type="tableSelect"],.tableHeaderMainMenuButton[data-type="tableCancel"]';
            cd.selectOperationModal.table.$.header.one('click', button, function(){
                cd.selectOperationModal.modal.hide();
                
                const $button = $( this ),
                      type = $button.attr('data-type');
                switch ( type ) {
                    case 'tableSelect': {
                        const selectId = cd.selectOperationModal.table.select.select;
                        resolve( selectId );
                    } break;
                    case 'tableCancel':
                        cd.selectOperationModal.modal.hide();
                        resolve( null );
                    break;
                }
            });
        };
        
        if ( !cd.selectOperationModal ) {
            fn.initSelectModal('オペレーション選択', 'operation_list').then(function( modal ){
                cd.selectOperationModal = modal;
                setClickEvent();
            });
        } else {
            cd.selectOperationModal.modal.show();
            setClickEvent();
        }
    });
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   conductorデータ更新・確認
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

updateConductorData() {
    const cd = this;

    if ( cd.setting.debug === true ) {
      window.console.group('Conductor data');
      window.console.log( cd.data );
      window.console.log( JSON.stringify( cd.data, null, '\t') );
      window.console.groupEnd('Conductor data');
    }

    // 変更があった場合のページ移動時処理フラグ
    // editor.confirmPageMove( true );
    cd.setting.setStorage = true;

    // カウンターを更新
    cd.data.config.nodeNumber = cd.count.node;
    cd.data.config.terminalNumber = cd.count.terminal;
    cd.data.config.edgeNumber = cd.count.edge;
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   conductorの保存と読み込み
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

/*
##################################################
  コンダクターパネルリセット
##################################################
*/
panelConductorReset() {
  const cd = this;
  cd.panelChange();
}
/*
##################################################
  コンダクターリセット
##################################################
*/
clearConductor() {
    const cd = this;
    
    // 選択を解除
    cd.nodeDeselect();
    // 全て消す
    cd.$.svgArea.empty();
    cd.$.artBoard.find('.node').remove();
    // カウンターリセット
    cd.count.node = 1;
    cd.count.terminal = 1;
    cd.count.edge = 1;
    // 履歴クリア
    cd.conductorHistory().clear();
    // LocalStorage削除
    fn.storage.remove('conductor-edit-temp');
    // 変更フラグリセット
    //editor.confirmPageMove( false );
    cd.setting.setStorage = false;
    // 初期値
    cd.setInitialConductorData();
    cd.canvasPositionReset(0);
    // パネル情報
    cd.panelChange();
    cd.panelConductorReset();
}
/*
##################################################
  ローカルストレージに保存する
##################################################
*/
saveConductor( saveConductorData ) {
    const cd = this;
    
    if ( cd.setting.setStorage === true ) {
      if ( cd.setting.debug === true ) {
        window.console.group('Set local strage');
        window.console.log( saveConductorData );
        window.console.log( JSON.stringify( saveConductorData, null, '\t') );
        window.console.groupEnd('Set local strage');
      }    
      fn.storage.set('conductor-edit-temp', saveConductorData );
    }
}
/*
##################################################
  再描画
##################################################
*/
selectConductor( result ) {
    const cd = this;
    
    cd.clearConductor();
    cd.loadConductor( result );
}
/*
##################################################
  読み込みイベント コールバック
##################################################
*/
readConductor( result ) {
    const cd = this;
    
    cd.clearConductor();
    try {
        cd.loadConductor( JSON.parse( result ) );
    } catch( e ) {
        window.console.error( e );
        //editor.log.set('error','JSON parse error.');
    }
}
/*
##################################################
  ノードリセット
##################################################
*/
nodeReSet( reSetConductorData ) {
    const cd = this;
    
    cd.$.editor.addClass('load-conductor');
    cd.setAction('editor-pause');
    
    // Nodeを再配置
    let readyCounter = 0;
    for ( const nodeID in reSetConductorData ) {
      if ( RegExp('^node-').test( nodeID ) ) {
        if ( nodeID === 'node-1') {
          if ( $('#node-1').length ) {
            $('#node-1').remove();
          }
        }
        const $node = cd.createNode( nodeID );
        cd.$.artBoard.append( $node );
        cd.nodeGemCheck( $node );
        cd.nodeSet( $node, reSetConductorData[ nodeID ].x, reSetConductorData[ nodeID ].y );
        
        // 分岐ノード
        const nodeCheck = ['merge', 'conditional-branch', 'parallel-branch', 'status-file-branch'];
        if ( nodeCheck.indexOf( reSetConductorData[ nodeID ].type ) !== -1 ) {
          readyCounter++;
          $node.ready( function() {
            cd.branchLine( nodeID );
            readyCounter--;
          });
        }
      }
    }

    // 完了チェック
    let timeoutCounter = 3000,
        loopCheckTime = 100;
    const loadComplete = function() {
      if ( readyCounter <= 0 ) {
        // Edge再接続
        try {
          for ( let edgeID in reSetConductorData ) {
            if ( RegExp('^line-').test( edgeID ) ) {
              cd.edgeConnect( edgeID );
            }
          }
        } catch( e ) {
          cd.message('1001');
          window.console.error( e );
        }
        cd.clearAction();
        cd.$.editor.removeClass('load-conductor');
        // 描画終了トリガー
        cd.$.window.trigger('conductorDrawEnd');
      } else {
        timeoutCounter = timeoutCounter - loopCheckTime;
        if ( timeoutCounter > 0 ) {
          setTimeout( loadComplete, loopCheckTime );
        } else {
          readyCounter = 0;
          loadComplete();
        }
      }
      // 作業確認時リザルトマークにイベントを付ける
      if ( cd.mode === 'checking') {
        cd.$.area.find('.node-result').on({
          'mouseenter': function(){
            const $result = $( this );
            $result.addClass('mouseenter');
          },
          'mouseleave': function(){
            $( this ).removeClass('mouseenter');
          },
          'click': function(){
            const $result = $( this ),
                  href = encodeURI( $result.attr('data-href') );
            if ( href !== '#') {
              open( href, '_blank') ;
            }
          }
        });
      }
    };
    loadComplete();
}
/*
##################################################
  コンダクターを読み込む
##################################################
*/
loadConductor( loadConductorData ) {
    const cd = this;
    
    if ( loadConductorData ) {
        cd.data = $.extend( true, {}, loadConductorData );
    }

    if ( cd.setting.debug === true ) {
        window.console.group('Get conductor data');
        window.console.log( cd.data );
        window.console.log( JSON.stringify( cd.data, null, '\t') );
        window.console.groupEnd('Get conductor data');
    }
    
    try {
      if ( cd.mode === 'edit') {
        // 読み込みデータはIDと追い越し判定用日時はリセットする
        cd.data['conductor'].id = null;
        cd.data['conductor'].last_update_date_time = null;
        cd.conductorMode('edit');
      }
      cd.count.node = cd.data.config.nodeNumber;
      cd.count.terminal = cd.data.config.terminalNumber;
      cd.count.edge = cd.data.config.edgeNumber;

      // Conductor情報
      const conductorID = cd.data['conductor'].id;
      if ( conductorID !== '' && conductorID !== null ) {
        $('#conductor-class-id').text( conductorID );
      } else {
        $('#conductor-class-id').text('Auto numbering');
      }
      let conductorNoteText = cd.data['conductor'].note;
      if ( conductorNoteText === undefined && conductorNoteText === null ) {
        conductorNoteText = '';
      }
      
      cd.nodeReSet( cd.data );
      cd.nodeViewAll( 0 );
    } catch( e ) {
      window.console.error( e );
      cd.clearAction();
      cd.$.editor.removeClass('load-conductor');
      cd.clearConductor();
      cd.message('1001');
       
      setTimeout( function(){
          alert('読み込み失敗');
      }, 1 );
    }
}

}