const car_interested = document.getElementById("car_id").getAttribute("car")
const form_email = document.querySelector('.email-form');
const btn_email = document.querySelector('.my-btn-email');
const csrf_email = document.getElementsByName('csrfmiddlewaretoken')
const confirmBox_email = document.getElementById('email-confirm-box');
const user_email = document.querySelector(".seller_info").getAttribute("seller-email")
const user_username = document.querySelector(".seller_info").getAttribute("seller-username")
console.log(form_email)

btn_email.addEventListener('click', event=>{
    form_email.addEventListener('submit', e=>{
        e.preventDefault()
        $.ajax({
            type: 'POST',
            url: '/send-email/',
            data:{
                'csrfmiddlewaretoken': csrf_email[0].value,
                'car_interested':car_interested,
                'seller_email': user_email,
                'seller_username': user_username,
            },
            success:function(response){
                confirmBox_email.innerHTML = "Wait answer of a seller"
            },
            error:function(error){
                confirmBox_email.innerHTML = "Upppss.. Something went wrong!!!"
            }
        })
    })
})