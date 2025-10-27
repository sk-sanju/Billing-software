from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from .models import Customer, Product, Invoice, InvoiceItem, Payment
from django.forms import modelform_factory, inlineformset_factory
from .utils import render_to_pdf

# -----------------------------------
# HOME VIEW
# -----------------------------------
def home(request):
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_invoices = Invoice.objects.count()
    total_revenue = sum(inv.total_amount for inv in Invoice.objects.all())

    context = {
        'total_customers': total_customers,
        'total_products': total_products,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
    }
    return render(request, 'core/home.html', context)

# -----------------------------------
# CUSTOMER CRUD
# -----------------------------------
CustomerForm = modelform_factory(Customer, fields='__all__')

def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'core/customer_list.html', {'customers': customers})

def customer_add(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('customer_list')
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Add Customer'})

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect('customer_list')
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Edit Customer'})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'core/customer_list.html', {'customer': customer})

# -----------------------------------
# PRODUCT CRUD
# -----------------------------------
ProductForm = modelform_factory(Product, fields='__all__')

def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'core/product_list.html', {'products': products})

def product_add(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Add Product'})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product'})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'core/product_list.html', {'product': product})

# -----------------------------------
# INVOICE + ITEMS
# -----------------------------------
InvoiceForm = modelform_factory(Invoice, fields=['customer', 'due_date'])
InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem,
    fields=('product', 'quantity', 'unit_price'),
    extra=1, can_delete=True
)

def generate_invoice_number():
    last_invoice = Invoice.objects.order_by('-id').first()
    if last_invoice:
        last_num = int(last_invoice.invoice_number.split('-')[-1])
        return f"INV-{last_num + 1:05d}"
    return "INV-00001"

@transaction.atomic
def invoice_add(request):
    invoice_form = InvoiceForm(request.POST or None)
    formset = InvoiceItemFormSet(request.POST or None)

    if invoice_form.is_valid() and formset.is_valid():
        invoice = invoice_form.save(commit=False)
        invoice.invoice_number = generate_invoice_number()
        invoice.save()
        formset.instance = invoice
        formset.save()

        # calculate total
        total = sum(item.total for item in invoice.items.all())
        invoice.total_amount = total
        invoice.save()

        return redirect('invoice_list')

    return render(request, 'core/invoice_form.html', {
        'invoice_form': invoice_form,
        'formset': formset,
        'title': 'Create Invoice'
    })

def invoice_list(request):
    invoices = Invoice.objects.select_related('customer').order_by('-date')
    return render(request, 'core/invoice_list.html', {'invoices': invoices})

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    payments = Payment.objects.filter(invoice=invoice)
    total_paid = sum(p.amount_paid for p in payments)
    balance = invoice.total_amount - total_paid

    return render(request, 'core/invoice_detail.html', {
        'invoice': invoice,
        'items': invoice.items.all(),
        'payments': payments,
        'total_paid': total_paid,
        'balance': balance
    })

# -----------------------------------
# PAYMENT SECTION
# -----------------------------------
PaymentForm = modelform_factory(Payment, fields=['amount_paid', 'payment_method', 'transaction_id'])

@transaction.atomic
def payment_add(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    form = PaymentForm(request.POST or None)

    if form.is_valid():
        payment = form.save(commit=False)
        payment.invoice = invoice
        payment.payment_date = timezone.now()
        payment.save()

        total_paid = sum(p.amount_paid for p in Payment.objects.filter(invoice=invoice))
        if total_paid >= invoice.total_amount:
            invoice.paid = True
        invoice.save()
        return redirect('invoice_detail', pk=invoice.id)

    return render(request, 'core/payment_form.html', {'form': form, 'invoice': invoice, 'title': 'Add Payment'})

def download_invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()
    payments = Payment.objects.filter(invoice=invoice)
    total_paid = sum(p.amount_paid for p in payments)
    balance = invoice.total_amount - total_paid

    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
        'total_paid': total_paid,
        'balance': balance,
    }

    pdf = render_to_pdf('core/invoice_pdf.html', context)
    filename = f"Invoice_{invoice.invoice_number}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
