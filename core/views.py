from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
import json
import datetime
from decimal import Decimal

# -----------------------------------
# HOME VIEW (DASHBOARD)
# -----------------------------------
def home(request):
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_invoices = Invoice.objects.count()
    
    # Total revenue is the sum of actual cash/payments received
    total_revenue = Payment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # Inventory Alerts
    out_of_stock_count = Product.objects.filter(stock=0).count()
    low_stock_count = Product.objects.filter(stock__gt=0, stock__lt=10).count()
    low_stock_products = Product.objects.filter(stock__lt=10).order_by('stock')[:5]
    
    # Recent Activities
    recent_invoices = Invoice.objects.select_related('customer').order_by('-date')[:5]
    recent_payments = Payment.objects.select_related('invoice__customer').order_by('-payment_date')[:5]
    
    # Analytics data (Daily sales for last 30 days)
    today = timezone.localdate()
    thirty_days_ago = today - datetime.timedelta(days=30)
    
    daily_sales = Invoice.objects.filter(date__date__gte=thirty_days_ago) \
        .annotate(day=TruncDate('date')) \
        .values('day') \
        .annotate(total=Sum('total_amount')) \
        .order_by('day')
    
    sales_labels = [item['day'].strftime('%Y-%m-%d') for item in daily_sales]
    sales_data = [float(item['total']) for item in daily_sales]
    
    context = {
        'total_customers': total_customers,
        'total_products': total_products,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
        'sales_labels': json.dumps(sales_labels),
        'sales_data': json.dumps(sales_data),
    }
    return render(request, 'core/home.html', context)
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
import json
import datetime

from .models import Customer, Product, Invoice, InvoiceItem, Payment
from .forms import CustomerForm, ProductForm, PaymentForm
from .utils import render_to_pdf

# -----------------------------------
# HOME VIEW (DASHBOARD)
# -----------------------------------
def home(request):
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_invoices = Invoice.objects.count()
    
    # Total revenue is the sum of actual cash/payments received
    total_revenue = Payment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0.00
    
    # Inventory Alerts
    out_of_stock_count = Product.objects.filter(stock=0).count()
    low_stock_count = Product.objects.filter(stock__gt=0, stock__lt=10).count()
    low_stock_products = Product.objects.filter(stock__lt=10).order_by('stock')[:5]
    
    # Recent Activities
    recent_invoices = Invoice.objects.select_related('customer').order_by('-date')[:5]
    recent_payments = Payment.objects.select_related('invoice__customer').order_by('-payment_date')[:5]
    
    # Analytics data (Daily sales for last 30 days)
    today = timezone.localdate()
    thirty_days_ago = today - datetime.timedelta(days=30)
    
    daily_sales = Invoice.objects.filter(date__date__gte=thirty_days_ago) \
        .annotate(day=TruncDate('date')) \
        .values('day') \
        .annotate(total=Sum('total_amount')) \
        .order_by('day')
    
    sales_labels = [item['day'].strftime('%Y-%m-%d') for item in daily_sales]
    sales_data = [float(item['total']) for item in daily_sales]
    
    context = {
        'total_customers': total_customers,
        'total_products': total_products,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
        'sales_labels': json.dumps(sales_labels),
        'sales_data': json.dumps(sales_data),
    }
    return render(request, 'core/home.html', context)

# -----------------------------------
# CUSTOMER CRUD & CRM
# -----------------------------------
def customer_list(request):
    q = request.GET.get('q', '')
    if q:
        customers = Customer.objects.filter(
            Q(name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q)
        ).order_by('-created_at')
    else:
        customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'core/customer_list.html', {'customers': customers, 'query': q})

def customer_add(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer added successfully!")
        return redirect('customer_list')
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Add Customer'})

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer profile updated!")
        return redirect('customer_list')
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Edit Customer'})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, "Customer record deleted.")
        return redirect('customer_list')
    return render(request, 'core/customer_list.html', {'customer': customer})

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    invoices = Invoice.objects.filter(customer=customer).order_by('-date')
    
    total_invoiced = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
    total_paid = Payment.objects.filter(invoice__customer=customer).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0.00
    balance = total_invoiced - total_paid
    
    # Calculate balance for each invoice
    for inv in invoices:
        inv.paid_amount = Payment.objects.filter(invoice=inv).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0.00
        inv.balance_amount = inv.total_amount - inv.paid_amount
        
    context = {
        'customer': customer,
        'invoices': invoices,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'balance': balance,
    }
    return render(request, 'core/customer_detail.html', context)

@require_POST
def customer_quick_add(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone', '')
        address = data.get('address', '')
        
        if not name or not email:
            return JsonResponse({'status': 'error', 'message': 'Name and Email are required fields.'}, status=400)
            
        if Customer.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'A customer with this email already exists.'}, status=400)
            
        customer = Customer.objects.create(name=name, email=email, phone=phone, address=address)
        return JsonResponse({
            'status': 'success',
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# -----------------------------------
# PRODUCT CRUD & INVENTORY
# -----------------------------------
def product_list(request):
    q = request.GET.get('q', '')
    if q:
        products = Product.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        ).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')
    return render(request, 'core/product_list.html', {'products': products, 'query': q})

def product_add(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Product added to inventory!")
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Add Product'})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Product details updated!")
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product'})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product removed from inventory.")
        return redirect('product_list')
    return render(request, 'core/product_list.html', {'product': product})

def product_list_json(request):
    products = list(Product.objects.all().values('id', 'name', 'price', 'stock'))
    return JsonResponse(products, safe=False)

# -----------------------------------
# INVOICE MODULE
# -----------------------------------
def generate_invoice_number():
    last_invoice = Invoice.objects.order_by('-id').first()
    if last_invoice:
        last_num = int(last_invoice.invoice_number.split('-')[-1])
        return f"INV-{last_num + 1:05d}"
    return "INV-00001"

@transaction.atomic
def invoice_add(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer_id = data.get('customer')
            due_date_str = data.get('due_date')
            subtotal = float(data.get('subtotal', 0))
            tax_rate = float(data.get('tax_rate', 0))
            tax_amount = float(data.get('tax_amount', 0))
            discount_amount = float(data.get('discount_amount', 0))
            total_amount = float(data.get('total_amount', 0))
            items_data = data.get('items', [])
            
            if not customer_id or not items_data:
                return JsonResponse({'status': 'error', 'message': 'Missing customer or invoice items.'}, status=400)
            
            customer = get_object_or_404(Customer, id=customer_id)
            due_date = None
            if due_date_str:
                due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
            invoice = Invoice(
                customer=customer,
                invoice_number=generate_invoice_number(),
                due_date=due_date,
                subtotal=subtotal,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                discount_amount=discount_amount,
                total_amount=total_amount
            )
            invoice.save()
            
            for item in items_data:
                product_id = item.get('product_id')
                quantity = int(item.get('quantity', 1))
                price = float(item.get('price'))
                
                product = get_object_or_404(Product, id=product_id)
                
                # Save item which will trigger stock deduction and total calculation
                invoice_item = InvoiceItem(
                    invoice=invoice,
                    product=product,
                    quantity=quantity,
                    unit_price=price
                )
                invoice_item.save()
            
            messages.success(request, f"Invoice {invoice.invoice_number} created successfully!")
            return JsonResponse({'status': 'success', 'invoice_id': invoice.id})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    # GET request
    customers = Customer.objects.all().order_by('name')
    products = Product.objects.all().order_by('name')
    products_json = json.dumps(list(products.values('id', 'name', 'price', 'stock')), default=str)
    
    context = {
        'customers': customers,
        'products_json': products_json,
        'title': 'Create Invoice'
    }
    return render(request, 'core/invoice_form.html', context)

def invoice_list(request):
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'all')
    
    invoices = Invoice.objects.select_related('customer').order_by('-date')
    
    if q:
        invoices = invoices.filter(
            Q(invoice_number__icontains=q) | Q(customer__name__icontains=q)
        )
        
    if status_filter == 'paid':
        invoices = invoices.filter(paid=True)
    elif status_filter == 'unpaid':
        invoices = invoices.filter(paid=False)
        
    # Annotate with paid payments and balance
    for inv in invoices:
        inv.paid_amount = Payment.objects.filter(invoice=inv).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
        inv.balance_amount = inv.total_amount - inv.paid_amount
        
    context = {
        'invoices': invoices,
        'query': q,
        'status_filter': status_filter
    }
    return render(request, 'core/invoice_list.html', context)

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

def invoice_delete(request, pk):
    """Delete an invoice (POST only)."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    messages.success(request, f"Invoice #{invoice.invoice_number} deleted successfully.")
    return redirect('invoice_list')

# -----------------------------------
# PAYMENTS SECTION
# -----------------------------------
@transaction.atomic
def payment_add(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    payments = Payment.objects.filter(invoice=invoice)
    total_paid = sum(p.amount_paid for p in payments)
    balance = invoice.total_amount - total_paid

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.payment_date = timezone.now()
            
            if payment.amount_paid > balance:
                form.add_error('amount_paid', f"Payment exceeds the remaining balance of ₹{balance}.")
            else:
                payment.save()
                
                # Check status
                new_total_paid = total_paid + payment.amount_paid
                if new_total_paid >= invoice.total_amount:
                    invoice.paid = True
                    invoice.save()
                    
                messages.success(request, f"Recorded payment of ₹{payment.amount_paid} for Invoice #{invoice.invoice_number}")
                return redirect('invoice_detail', pk=invoice.id)
    else:
        form = PaymentForm(initial={'amount_paid': balance})

    return render(request, 'core/payment_form.html', {
        'form': form,
        'invoice': invoice,
        'balance': balance,
        'title': 'Add Payment'
    })

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
    if pdf:
        filename = f"Invoice_{invoice.invoice_number}.pdf"
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse("Error generating PDF invoice", status=500)
