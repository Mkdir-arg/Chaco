function deleteArchivo(id) {
    $.ajax({

        // Función Ajax para eliminar la archivos
        url: deleteUrl,
        data: {
            'id': id,
        },
        dataType: 'json',
        success: function (data) {
            if (data.deleted) {
                $("#tr-" + id).remove();
                window.ChacoToast?.show(data.mensaje, { type: data.tipo_mensaje });
            }
        },
        error: (err) => {
            window.ChacoToast?.error(err);
        }
    });
};
