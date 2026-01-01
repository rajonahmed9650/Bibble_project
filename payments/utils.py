from django.utils import timezone
from payments.models import Subscription, Package

class SubscriptionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # শুধু logged-in user এর জন্য
        if user.is_authenticated:
            sub = Subscription.objects.filter(
                user=user,
                is_active=True
            ).first()

            if (
                sub and
                sub.expired_at and
                sub.expired_at < timezone.now()
            ):
                # EXPIRED → AUTO DEACTIVATE
                free_pkg = Package.objects.filter(package_name="free").first()

                sub.is_active = False
                sub.current_plan = "free"
                sub.package = free_pkg
                sub.save(update_fields=["is_active", "current_plan", "package"])

        return self.get_response(request)



from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils import timezone


def draw_dashed_line(c, x1, x2, y):
    c.setDash(3, 3)
    c.setLineWidth(0.4)
    c.line(x1, y, x2, y)
    c.setDash()  # reset


def generate_invoice_pdf(invoice):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="invoice_{invoice.id}.pdf"'
    )

    c = canvas.Canvas(response, pagesize=A5)
    width, height = A5

    left = 40
    right = width - 40
    y = height - 40

    # ==========================
    # HEADER
    # ==========================
    c.setFont("Courier-Bold", 16)
    c.drawCentredString(width / 2, y, "*** PAYMENT RECEIPT ***")
    y -= 15

    draw_dashed_line(c, left, right, y)
    y -= 20

    # ==========================
    # BASIC INFO
    # ==========================
    c.setFont("Courier", 9)
    c.drawString(left, y, f"Invoice ID : {invoice.id}")
    y -= 12
    c.drawString(left, y, f"Transaction_id: {invoice.transaction_id}")
    y -= 12
    c.drawString(left, y, f"Date       : {invoice.payment_date.strftime('%Y-%m-%d')}")
    y -= 15

    draw_dashed_line(c, left, right, y)
    y -= 20

    # ==========================
    # CUSTOMER
    # ==========================
    c.setFont("Courier-Bold", 9)
    c.drawString(left, y, "BILLED TO")
    y -= 12

    c.setFont("Courier", 9)
    c.drawString(left, y, invoice.user.email)
    y -= 15

    draw_dashed_line(c, left, right, y)
    y -= 20

    # ==========================
    # SUBSCRIPTION DETAILS
    # ==========================
    c.setFont("Courier-Bold", 9)
    c.drawString(left, y, "SUBSCRIPTION")
    y -= 12

    c.setFont("Courier", 9)
    c.drawString(left, y, f"Package : {invoice.package.package_name if invoice.package else 'N/A'}")
    y -= 12
    c.drawString(left, y, f"Plan    : {invoice.plan.capitalize()}")
    y -= 12
    c.drawString(
        left,
        y,
        f"Period  : {invoice.start_date.date()} → {invoice.end_date.date()}",
    )
    y -= 15

    draw_dashed_line(c, left, right, y)
    y -= 20

    # ==========================
    # PAYMENT SUMMARY
    # ==========================
    c.setFont("Courier-Bold", 9)
    c.drawString(left, y, "PAYMENT SUMMARY")
    y -= 15

    c.setFont("Courier", 9)
    c.drawString(left, y, "Amount Paid")
    c.drawRightString(right, y, f"${invoice.amount}")
    y -= 12


    draw_dashed_line(c, left, right, y)
    y -= 20

    # ==========================
    # FOOTER
    # ==========================
    c.setFont("Courier-Bold", 9)
    c.drawCentredString(width / 2, y, "THANK YOU FOR YOUR PAYMENT!")
    y -= 15

    c.setFont("Courier", 8)
    c.drawCentredString(
        width / 2,
        y,
        f"Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
    )

    c.showPage()
    c.save()
    return response
