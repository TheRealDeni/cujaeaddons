odoo.define('survey_upload_file', function (require) {
    'use strict';

    var SurveyFormWidget = require('survey.form');
    var core = require('web.core');
    var _t = core._t;

    SurveyFormWidget.include({
        events: _.extend({}, SurveyFormWidget.prototype.events,{
            'change .o_survey_upload_file': '_onFileChange',
        }),

        _onFileChange: function(event) {
            var self = this;
            var files = event.target.files;
            var fileNames = [];
            var dataURLs = [];
            var allowedExtensions = new Set([
                'doc', 'docx', 'ppt', 'pptx', 
                'xls', 'xlsx', 'pdf', 'jpg', 
                'jpeg', 'png', 'gif', 'zip', 'rar'
            ]);
            var maxSizeMB = 10;
            
            // Validación inicial
            for (let i = 0; i < files.length; i++) {
                let file = files[i];
                let extension = file.name.split('.').pop().toLowerCase();
                
                // Verificar extensión
                if (!allowedExtensions.has(extension)) {
                    this._showFileError(_t("Tipo de archivo no permitido. Formatos válidos: ") +
                        Array.from(allowedExtensions).join(', '));
                    event.target.value = '';
                    return;
                }
                
                // Verificar tamaño (10MB en bytes)
                if (file.size > maxSizeMB * 1024 * 1024) {
                    this._showFileError(_t("El archivo excede el límite de ") + maxSizeMB + "MB");
                    event.target.value = '';
                    return;
                }
            }

            // Procesar archivos válidos
            for (let i = 0; i < files.length; i++) {
                let file = files[i];
                let reader = new FileReader();
                
                reader.onload = function(e) {
                    let dataURL = e.target.result.split(',')[1];
                    fileNames.push(file.name);
                    dataURLs.push(dataURL);

                    if (fileNames.length === files.length) {
                        self._updateFileUI(event.target, dataURLs, fileNames);
                    }
                };
                reader.readAsDataURL(file);
            }
        },

        _showFileError: function(message) {
            core.bus.trigger('notification', {
                type: 'warning',
                title: _t("Error de Validación"),
                message: message
            });
        },

        _updateFileUI: function(inputElement, dataURLs, fileNames) {
            var $input = $(inputElement);
            $input.attr('data-oe-data', JSON.stringify(dataURLs));
            $input.attr('data-oe-file_name', JSON.stringify(fileNames));

            var fileList = document.getElementById('fileList');
            fileList.innerHTML = '';

            var ul = document.createElement('ul');
            fileNames.forEach(function(fileName) {
                var li = document.createElement('li');
                li.textContent = fileName;
                ul.appendChild(li);
            });

            var deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-danger btn-sm mt-2';
            deleteBtn.textContent = _t('Eliminar Todos');
            deleteBtn.addEventListener('click', function() {
                fileList.innerHTML = '';
                $input.attr({'data-oe-data': '', 'data-oe-file_name': ''});
                $input.val('');
            });

            fileList.appendChild(ul);
            fileList.appendChild(deleteBtn);
        },

        _prepareSubmitValues: function (formData, params) {
            this._super(formData, params);
            this.$('[data-question-type]').each(function () {
                if ($(this).data('questionType') === 'upload_file') {
                    params[this.name] = [
                        $(this).data('oe-data') || [],
                        $(this).data('oe-file_name') || []
                    ];
                }
            });
        },
    });
});